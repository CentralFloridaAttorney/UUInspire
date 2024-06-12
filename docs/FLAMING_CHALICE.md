### Session 1: Creating a Flaming Chalice in Unity WebGL

## Welcome

Welcome to the first session of the UU Inspire Learning Group! In this session, we will create a beautiful Unitarian Universalist flaming chalice as a prefab in Unity and deploy it using Unity WebGL. This README will guide you through the steps of modeling, texturing, setting up the prefab with a flame effect, and deploying it using Unity WebGL.

---

## Prerequisites

Before starting this project, please ensure you have the necessary software installed on your computer. Follow the instructions in our [Software Installation Guide](PREREQUISITES.md).

---

## Objectives

- Model a chalice in Blender
- Texture the chalice in GIMP
- Set up the chalice prefab with a flame effect in Unity
- Deploy the project using Unity WebGL

---

## Project Overview

In this session, you will:
- Model the chalice in Blender
- Texture the chalice in GIMP
- Set up the chalice prefab with a flame effect in Unity
- Deploy the project using Unity WebGL

---

## Steps to Follow

### Step 1: Model the Chalice in Blender

1. **Create the Chalice Base:**
   - In Blender, delete the default cube by selecting it and pressing `X`.
   - Add a new cylinder by pressing `Shift + A` and selecting **Mesh > Cylinder**.
   - Scale and position the cylinder to form the base of the chalice.
   - Use the **Extrude** tool (`E`) to create the stem and the bowl of the chalice.

2. **Refine the Shape:**
   - Switch to **Edit Mode** (`Tab` key).
   - Select vertices, edges, or faces to adjust the shape as needed.
   - Use the **Loop Cut** tool (`Ctrl + R`) to add more geometry and refine the shape.

3. **Smooth the Surface:**
   - In **Object Mode**, right-click the chalice and select **Shade Smooth**.
   - Add a **Subdivision Surface** modifier from the **Modifier** panel to further smooth the surface.

4. **Export the Model:**
   - Save your Blender file.
   - Export the model as an FBX file by going to **File > Export > FBX**.
   - Save the FBX file in a location where you can easily find it.

### Step 2: Texture the Chalice in GIMP

1. **Create the Texture:**
   - In GIMP, create a new image with dimensions 1024x1024 pixels.
   - Design a texture for the chalice, incorporating elements like gold or silver coloring, and any symbolic designs you prefer.

2. **Save the Texture:**
   - Save the image as a PNG file.
   - Save the PNG file in the same location as your FBX file.

### Step 3: Set Up the Chalice Prefab in Unity

1. **Import Assets:**
   - In Unity, right-click in the **Project** window and select **Import New Asset**.
   - Import the FBX model and PNG texture you created.

2. **Create the Material:**
   - Right-click in the **Project** window and select **Create > Material**.
   - Name the material `ChaliceMaterial`.
   - Assign the PNG texture to the **Albedo** property of the material.

3. **Apply the Material:**
   - Drag the FBX model into the **Scene** view.
   - Select the model in the **Hierarchy** window.
   - In the **Inspector** window, assign the `ChaliceMaterial` to the **Mesh Renderer** component.

4. **Create the Flame Effect:**
   - Right-click in the **Project** window and select **Create > Particle System**.
   - Position the particle system above the chalice bowl to simulate a flame.
   - Customize the particle system settings to create a realistic flame effect. Adjust parameters such as **Start Color**, **Start Size**, **Lifetime**, and **Emission Rate** to achieve the desired look.

5. **Create the Prefab:**
   - Drag the chalice model and the particle system from the **Hierarchy** window into the **Project** window to create a prefab.
   - Name the prefab `FlamingChalicePrefab`.

6. **Save the Scene:**
   - Save the scene by going to **File > Save Scene**.
   - Name the scene `MainScene`.

### Step 4: Deploy the Project Using Unity WebGL

1. **Set Up WebGL Build:**
   - Go to **File > Build Settings**.
   - Select **WebGL** from the platform list and click **Switch Platform**.

2. **Configure Build Settings:**
   - Click on **Player Settings** and adjust the settings as needed, such as the resolution and the WebGL template.

3. **Build and Run:**
   - Click on **Build and Run** to deploy the project. Choose a location to save the build files.
   - Unity will build the project and open it in your default web browser.

---

## Resources

- **Unity Learn:** <a href="https://learn.unity.com/" target="_blank">Unity Learn</a>
- **Blender Tutorials:** <a href="https://www.blenderguru.com/" target="_blank">Blender Guru</a>
- **GIMP Tutorials:** <a href="https://www.gimp.org/tutorials/" target="_blank">GIMP Documentation</a>

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Thank you for being a part of UU Inspire. Let's spark creativity and innovation together!
```

Save this content in the `docs` folder as `README.md`. This setup provides clear instructions for creating a flaming chalice and ensures everyone has the necessary resources to get started.