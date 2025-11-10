import torch
import torch.nn as nn
import torchvision.transforms as T
import numpy as np
import cv2

from nets.funiegan import GeneratorFunieGAN as Generator  # adjust import path to match your repo

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
to_image = T.ToPILImage()

# --- Open camera ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame (BGR->RGB)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    inp = to_tensor(rgb).unsqueeze(0).to(device)

    # Run enhancement
    with torch.no_grad():
        out = G(inp)

    # Convert back to OpenCV format
    out_np = out.squeeze(0).cpu().permute(1, 2, 0).numpy()
    out_np = np.clip(out_np * 255, 0, 255).astype(np.uint8)
    out_bgr = cv2.cvtColor(out_np, cv2.COLOR_RGB2BGR)

    # Resize for display
    out_bgr = cv2.resize(out_bgr, (frame.shape[1], frame.shape[0]))

    # Show both
    cv2.imshow("Original", frame)
    cv2.imshow("Enhanced", out_bgr)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()