class funie_gan:
    # FUnIE-GAN
    # --- Load pretrained FUnIE-GAN model ---
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_path = "funie_generator.pth"  # change if different
    G = Generator().to(device)
    G.load_state_dict(torch.load(model_path, map_location=device))
    G.eval()

    # --- Define transforms ---
    to_tensor = T.Compose([
        T.ToPILImage(),
        T.Resize((256, 256)),
        T.ToTensor()
    ])
