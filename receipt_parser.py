import torch
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import json
import time
import warnings
import os
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports

def fixed_get_imports(filename: str | os.PathLike) -> list[str]:
    """Intercepts the model's import check and deletes flash_attn from the list"""
    if not str(filename).endswith("modeling_florence2.py"):
        return get_imports(filename)
    imports = get_imports(filename)
    if "flash_attn" in imports:
        imports.remove("flash_attn")
    return imports

warnings.filterwarnings("ignore")

# Setup the Vision Model
MODEL_ID = "microsoft/Florence-2-base"
print("Loading Florence-2 Vision Model...")

# Using GPU acceleration 
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Hardware acceleration: {device.upper()}")

with patch("transformers.dynamic_module_utils.get_imports", fixed_get_imports):
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, trust_remote_code=True).to(device).eval()
    
processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)

def ask_image(image, question):
    """Sends an image and a text question to Florence-2"""
    prompt = question 
    
    # Prepare the inputs for the GPU
    inputs = processor(text=prompt, images=image, return_tensors="pt").to(device)
    
    # Generate the answer
    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=1024,
        do_sample=False,
        num_beams=3
    )
    
    # Decode the output and strip out the special AI tags
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    return generated_text.strip()

def get_image_text(image_path):
    """Agent 1: Florence-2 extracts raw text using its native OCR task"""
    image = Image.open(image_path).convert("RGB")
    
    prompt = "<OCR>" 
    inputs = processor(text=prompt, images=image, return_tensors="pt").to(device)
    
    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=1024,
        do_sample=False,
        num_beams=3
    )
    
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text.strip()

def extract_receipt_data(image_path):
    print(f"\nVision Agent (Florence-2) scanning {image_path.split('/')[-1]}...")
    raw_text = get_image_text(image_path)
    print(f"   Raw Text Found: {raw_text}")
    
    print("Text Agent (Llama 3) formatting data...")
    # Initialize Llama 3 to format the output
    llm = ChatOllama(model="llama3", temperature=0, format="json")
    
    # System Prompt
    prompt = ChatPromptTemplate.from_template("""
    Extract the following information from the raw OCR text of a receipt.
    Return ONLY a valid JSON object with these exact keys: "vendor", "transaction_id", "amount".
    Strip out any dollar signs ($) from the amount.
    
    Raw OCR Text: {text}
    """)
    
    chain = prompt | llm | JsonOutputParser()
    
    # Execute the chain
    structured_data = chain.invoke({"text": raw_text})
    
    # Add the filename back in for the records
    structured_data["file"] = image_path.split('/')[-1]
    
    return structured_data

if __name__ == "__main__":
    test_images = [
        "audit_files/receipts/receipt_TXN-1004.png", 
        "audit_files/receipts/receipt_TXN-1003.png"  
    ]
    
    print("-" * 50)
    start_time = time.time()
    
    for img_path in test_images:
        structured_data = extract_receipt_data(img_path)
        print("\nFinal Structured Output:")
        print(json.dumps(structured_data, indent=4))
        print("-" * 50)
        
    print(f"Full pipeline complete in {time.time() - start_time:.2f} seconds.")