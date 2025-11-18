import torch
import torch.nn as nn
import torchvision.transforms as T

from image_enhancement.nets.funiegan import GeneratorFunieGAN as Generator  # adjust import path to match your repo

def funie():
    # FUnIE-GAN
    # --- Load pretrained FUnIE-GAN model ---
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_path = "image_enhancement/funie_generator.pth"  # change if different
    G = Generator().to(device)
    G.load_state_dict(torch.load(model_path, map_location=device))
    G.eval()

    # --- Define transforms ---
    to_tensor = T.Compose([
        T.ToPILImage(),
        T.Resize((256, 256)),
        T.ToTensor()
    ])
    return {
        "generator" : G,
        "transformer" : to_tensor
    }
