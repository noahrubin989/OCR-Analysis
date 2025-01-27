from dotenv import load_dotenv
import os
from PIL import Image, ImageDraw
from matplotlib import pyplot as plt

# Azure SDK imports
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

def setup_client():
    """
    Sets up and returns an ImageAnalysisClient
    using credentials from environment variables.
    """
    load_dotenv()
    endpoint = os.getenv('AI_SERVICE_ENDPOINT')
    key = os.getenv('AI_SERVICE_KEY')
    credential = AzureKeyCredential(key=key)

    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=credential
    )
    return client


def read_image(image_file):
    """
    Reads an image file and returns its byte content.
    """
    with open(image_file, "rb") as f:
        return f.read()


def perform_ocr(client, image_file):
    """
    Given an ImageAnalysisClient and an image file path,
    performs text extraction (OCR) on the image and
    displays bounding polygons for recognized text.
    """
    print(f"\nPerforming OCR on {image_file}\n")

    # Read the image file as bytes
    image_data = read_image(image_file)

    # Use analyze function to read text in the image
    result = client.analyze(
        image_data=image_data,
        visual_features=[VisualFeatures.READ]
    )

    # Display the image and overlay it with the extracted text
    if result.read is not None and result.read.blocks:
        print("Text Detected:")

        # Load the image for display and drawing
        pil_image = Image.open(image_file)
        fig = plt.figure(figsize=(pil_image.width / 100, pil_image.height / 100))
        plt.axis('off')
        draw = ImageDraw.Draw(pil_image)
        color = 'cyan'

        # Each block can contain multiple lines
        for block in result.read.blocks:
            for line in block.lines:
                # Print the detected text
                print(f"  {line.text}")

                # Draw bounding polygon for each line
                r = line.bounding_polygon
                bounding_polygon = (
                    (r[0].x, r[0].y),
                    (r[1].x, r[1].y),
                    (r[2].x, r[2].y),
                    (r[3].x, r[3].y)
                )
                # print("   Bounding Polygon:", bounding_polygon)
                draw.polygon(bounding_polygon, outline=color, width=3)

        # Ensure output folder exists
        output_folder = 'output_images'
        os.makedirs(output_folder, exist_ok=True)

        # Create a filename for the output
        base_name = os.path.basename(image_file)          # e.g. 'Lincoln.jpg'
        file_root, _ = os.path.splitext(base_name)        # e.g. ('Lincoln', '.jpg')
        output_filename = f"text_{file_root}.jpg"         # e.g. 'text_Lincoln.jpg'
        output_path = os.path.join(output_folder, output_filename)

        # Show and save image with overlays
        plt.imshow(pil_image)
        plt.tight_layout(pad=0)
        fig.savefig(output_path)
        print(f'\n  Results saved in {output_path}')


def main():
    try:
        # Set up client
        cv_client = setup_client()

        # Menu for text reading functions
        print('\n1: Use Read API on images in the "images" folder')
        print('Any other key to quit\n')

        command = input('Enter a number: ')

        if command == '1':
            # Create a list of potential image files (add or remove extensions as needed)
            valid_extensions = {'.jpg', '.jpeg', '.png'}
            images = [
                f for f in os.listdir('images')
                if os.path.splitext(f)[1].lower() in valid_extensions
            ]

            for image_name in images:
                image_file = os.path.join('images', image_name)
                perform_ocr(cv_client, image_file)
        else:
            print("Exiting...")

    except Exception as ex:
        print(f"An error occurred: {ex}")

if __name__ == "__main__":
    main()
