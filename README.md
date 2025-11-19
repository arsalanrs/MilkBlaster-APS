# MilkBlaster - Retro Cow Chase Adventure 🐄

A retro-style platformer game built with Python and Pygame where you play as a stickman trying to collect cookies while avoiding an angry cow!

## 🎮 Game Overview

Retro Cow Chase Adventure is a challenging 5-level adventure game that combines platforming, puzzle-solving, and action elements. Your goal is to navigate through various levels, collect cookies, and avoid the pursuing cow!

## ✨ Features

- **5 Unique Levels**: Each level offers different gameplay mechanics and challenges
- **Animated Characters**: Smooth stickman animation using GIF frames and custom cow artwork
- **Custom Graphics**: Beautiful backgrounds and block textures for level 1
- **Multiple Game Modes**: Platforming, puzzle-solving, decision-making, and combat
- **Retry System**: 3 attempts per level before returning to menu

## 📋 Requirements

- Python 3.6 or higher
- Pygame
- Pillow (PIL)

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/arsalanrs/MilkBlaster-APS.git
cd MilkBlaster-APS
```

2. Install the required dependencies:
```bash
pip install pygame pillow
```

## 🚀 How to Run

Simply run the game file:
```bash
python milkblaster_main.py
```

## 🎯 Controls

- **Arrow Keys**: Move left/right
- **Space**: Jump (Level 1, 5) / Shoot (Level 5)
- **1-7 Keys**: Cut wires (Level 2)
- **A/B Keys**: Make decision (Level 3)
- **Right Arrow**: Move forward during green light (Level 4)
- **Up Arrow**: Jump (Level 5)
- **Enter**: Confirm/Continue

## 📖 Game Levels

### Level 1: Obstacle Course
- Navigate through platforms and collect all cookies
- Avoid the pursuing cow
- Use your jumping skills to reach higher platforms

### Level 2: Bomb Defusal
- Cut wires in the correct rainbow order (ROYGBIV)
- One wrong wire and it's game over!

### Level 3: Decision Time
- Make a crucial choice that affects your journey
- Choose wisely!

### Level 4: Red/Green Light
- Move only during green light
- Stay still during red light or face the consequences
- Reach the goal to advance

### Level 5: Final Standoff
- Battle the cow in an epic showdown
- Jump to dodge attacks and shoot to defeat the cow
- The cow has 3 lives - can you survive?

## 📁 File Structure

```
MilkBlaster-APS/
├── chatgpt_game2.py       # Main game file
├── bglevel1.jpeg          # Level 1 background
├── lv1blocks.jpeg         # Level 1 platform blocks
├── Cow_cartoon_04.svg.png # Cow character sprite
├── output-onlinegiftools.gif  # Stickman animation
├── 1ee617f89cec2e319198dd1caa6fea67.gif  # Additional animation
└── README.md              # This file
```

## 🎨 Assets

The game uses custom graphics including:
- Custom level 1 background (`bglevel1.jpeg`)
- Custom platform blocks (`lv1blocks.jpeg`)
- Animated stickman character
- Cartoon cow enemy

## 🐛 Known Issues

- Sound effects and background music are commented out (can be enabled by adding audio files)

## 📝 License

This project is open source and available for educational purposes.

## 👤 Author

**arsalanrs**
- GitHub: [@arsalanrs](https://github.com/arsalanrs)

## 🙏 Acknowledgments

Built with Pygame - A Python library for creating games.

---

**Enjoy the game and watch out for that cow! 🐄🥛**

