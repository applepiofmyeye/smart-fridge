import requests
import os
from pathlib import Path

class FruitClassifierClient:
    def __init__(self, server_url="http://192.168.1.59:5000"):
        """
        Initialize the client with the server URL
        
        Args:
            server_url (str): The base URL of the Flask server
        """
        self.server_url = server_url
        self.upload_endpoint = f"{server_url}/upload"

    def process_image(self, image_path):
        """
        Send an image to the server for classification
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Server response containing prediction results
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            with open(image_path, 'rb') as image_file:
                files = {'file': (Path(image_path).name, image_file, 'image/jpeg')}
                response = requests.post(self.upload_endpoint, files=files)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "error": f"Server returned status code {response.status_code}",
                        "message": response.text
                    }
                    
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to connect to server: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

def main():
    """
    Example usage of the FruitClassifierClient
    """
    # Initialize client
    client = FruitClassifierClient()

    classes = ["fresh apple", "rotten apple", "fresh banana", "rotten banana", "fresh cucumber", "rotten cucumber", "fresh orange", "rotten orange", "fresh potato", "rotten potato", "fresh tomato", "rotten tomato"]
    
    # Example folder containing images
    image_folder = "test_images"
    try:
    
    # Process all jpg/jpeg images in the folder
        if os.path.exists(image_folder):
            for image_file in os.listdir(image_folder):
                if image_file.lower().endswith(('.png', '.jpeg')):
                    image_path = os.path.join(image_folder, image_file)
                    print(f"\nProcessing {image_file}...")
                    
                    results = client.process_image(image_path)
                    print(results)
                    
                    if "success" in results:
                        for result in results["predictions"]:
                            print(f"Predicted Result: {classes[int(result['class_id'])]}") 
                            print(f"Confidence: {result['confidence']:.2f}")
                            print(f"Raw prediction: {result}")
                    else:
                        print(f"Error!")
        else:
            print(f"Image folder '{image_folder}' not found!")
    except Exception as e: 
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()