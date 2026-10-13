#!/usr/bin/env python3
"""Trace white face, hair, eyebrow, and ear regions on a black background."""
from pathlib import Path
from PIL import Image, ImageDraw

bundle = Path(__file__).resolve().parents[1] / 'content/posts/2025-10-23-hopfield-simulation'
source = Image.open(bundle / 'pattern2.png')

# Face silhouettes traced from the input; shadows inside the face are discarded.
scale = 3
result = Image.new('L', (256 * scale, 256 * scale), 0)
draw = ImageDraw.Draw(result)

def points(coordinates):
    return [(round(x * scale), round(y * scale)) for x, y in coordinates]

def line(coordinates, fill=0, width=1):
    draw.line(points(coordinates), fill=fill, width=round(width * scale), joint='curve')

# Fill hair and the visible ear before drawing the face and separating contours.
left_hair = [(25, 0), (122, 0), (143, 15), (133, 0), (163, 0), (193, 14),
             (180, 30), (154, 39), (132, 59), (108, 82), (92, 89), (74, 80),
             (58, 64), (45, 82), (35, 96), (34, 77), (39, 50), (47, 27)]
right_hair = [(188, 13), (196, 15), (202, 47), (213, 83), (224, 112),
              (229, 128), (222, 151), (208, 187), (194, 223), (183, 256),
              (168, 256), (176, 235), (187, 210), (198, 179), (206, 150),
              (206, 125), (200, 99), (192, 74), (185, 48), (181, 29)]
ear = [(229, 18), (240, 14), (248, 14), (255, 17), (255, 127),
       (247, 130), (240, 128), (237, 108), (234, 86), (231, 63)]
for region in [left_hair, right_hair, ear]:
    draw.polygon(points(region), fill=255)

forehead = [(58, 58), (86, 8), (120, 29), (128, 31), (107, 58), (91, 68), (89, 76), (73, 68)]
face = [(155, 38), (182, 44), (190, 68), (195, 86), (202, 108), (207, 126),
        (208, 145), (202, 170), (192, 196), (181, 220), (172, 240), (167, 256),
        (130, 256), (130, 244), (142, 237), (146, 224), (136, 229), (113, 234),
        (114, 207), (140, 195), (177, 181), (167, 177), (146, 180), (113, 191),
        (95, 199), (84, 197), (70, 189), (87, 179), (98, 161), (81, 168),
        (50, 184), (42, 182), (94, 91), (107, 82), (125, 68), (140, 58)]
draw.polygon(points(forehead), fill=255)
draw.polygon(points(face), fill=255)

# Outline white regions so adjacent face, hair, and eyebrow shapes remain distinct.
line(forehead + [forehead[0]], width=1.4)
line(face + [face[0]], width=1.4)
brow = [(108, 83), (138, 68), (166, 52), (182, 44), (175, 57),
        (149, 76), (122, 88)]
draw.polygon(points(brow), fill=255)
line(brow + [brow[0]], width=1.2)

# Keep the eye, nose, lips, and chin details as a small number of strokes.
line([(72, 58), (82, 69), (94, 77)], width=1.5)
line([(117, 88), (130, 94), (143, 95), (155, 96)], width=2)
line([(103, 91), (91, 109), (80, 134), (62, 162), (48, 180)], width=1.3)
line([(100, 150), (109, 145), (115, 145), (117, 147), (114, 155)], width=1.2)
line([(97, 165), (89, 175), (83, 179)], width=1.2)
line([(88, 193), (114, 187), (141, 177), (158, 173), (171, 175), (181, 182)], width=1.8)
line([(91, 196), (112, 193), (139, 184), (158, 178), (172, 178)], width=1)
line([(118, 185), (120, 190)], width=1)
line([(139, 178), (140, 184)], width=1)
line([(156, 175), (157, 180)], width=1)
line([(115, 230), (132, 226), (145, 219), (155, 215)], width=1.2)

# Black strand lines and ear folds preserve recognizable edges without shading.
line([(54, 0), (44, 26), (36, 56), (35, 81)], width=1.2)
line([(89, 0), (121, 27), (130, 30), (113, 52), (96, 68)], width=1.3)
line([(162, 0), (173, 16), (187, 26)], width=1.2)
line([(193, 34), (203, 69), (216, 105), (224, 127)], width=1.1)
line([(213, 153), (204, 180), (193, 210), (178, 256)], width=1.2)
line(ear + [ear[0]], width=1.2)
line([(231, 32), (241, 29), (249, 33), (255, 39)], width=1)
line([(234, 49), (242, 47), (249, 52), (255, 58)], width=1)
line([(237, 73), (247, 70), (253, 75), (255, 80)], width=1)
line([(240, 106), (249, 102), (255, 104)], width=1)

# Supersampling makes continuous contours; final threshold gives exactly two colors.
result = result.resize(source.size, Image.Resampling.LANCZOS)
result = result.point(lambda value: 255 if value >= 128 else 0)
output = bundle / 'pattern2-binary.png'
result.save(output, optimize=True)
print(f'Generated {output.name}: {source.width} × {source.height}, white face/hair/ear and black outlines on black.')
