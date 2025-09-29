<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>VFX Crater</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-black text-white font-sans">

  <!-- Navbar -->
  <header class="flex justify-between items-center p-6">
    <h1 class="text-2xl font-bold">VFX Crater</h1>
    <nav>
      <ul class="flex space-x-6">
        <li><a href="#services" class="hover:text-gray-400">Services</a></li>
        <li><a href="#portfolio" class="hover:text-gray-400">Portfolio</a></li>
        <li><a href="#contact" class="hover:text-gray-400">Contact</a></li>
      </ul>
    </nav>
  </header>

  <!-- Hero Section -->
  <section class="flex flex-col items-center text-center p-12">
    <h2 class="text-4xl md:text-6xl font-bold mb-4">Cinematic VFX & Motion Graphics</h2>
    <p class="max-w-2xl mb-6 text-gray-300">We bring imagination to reality with stunning CGI, 3D animation, and creative motion visuals.</p>
    <a href="#contact" class="bg-red-600 px-6 py-3 rounded-full hover:bg-red-800">Get in Touch</a>
  </section>

  <!-- Services -->
  <section id="services" class="p-12">
    <h3 class="text-3xl font-bold mb-8 text-center">Our Services</h3>
    <div class="grid md:grid-cols-3 gap-6">
      <div class="bg-gray-900 p-6 rounded-xl shadow-lg">
        <h4 class="text-xl font-semibold mb-2">3D Animation</h4>
        <p class="text-gray-400">High-quality 3D motion design, cinematic animations, and product visuals.</p>
      </div>
      <div class="bg-gray-900 p-6 rounded-xl shadow-lg">
        <h4 class="text-xl font-semibold mb-2">Compositing</h4>
        <p class="text-gray-400">Advanced VFX compositing, green screen removal, and seamless integration.</p>
      </div>
      <div class="bg-gray-900 p-6 rounded-xl shadow-lg">
        <h4 class="text-xl font-semibold mb-2">Motion Graphics</h4>
        <p class="text-gray-400">Engaging titles, cinematic intros, and professional logo animations.</p>
      </div>
    </div>
  </section>

  <!-- Portfolio -->
  <section id="portfolio" class="p-12 bg-gray-950">
    <h3 class="text-3xl font-bold mb-8 text-center">Portfolio</h3>
    <div class="grid md:grid-cols-3 gap-6">
      <img src="https://via.placeholder.com/400x250" class="rounded-lg shadow-lg" alt="Project 1">
      <img src="https://via.placeholder.com/400x250" class="rounded-lg shadow-lg" alt="Project 2">
      <img src="https://via.placeholder.com/400x250" class="rounded-lg shadow-lg" alt="Project 3">
    </div>
  </section>

  <!-- Contact -->
  <section id="contact" class="p-12 text-center">
    <h3 class="text-3xl font-bold mb-4">Contact Us</h3>
    <p class="mb-6 text-gray-400">Let’s create something amazing together!</p>
    <a href="mailto:info@vfxcrater.com" class="bg-red-600 px-6 py-3 rounded-full hover:bg-red-800">info@vfxcrater.com</a>
  </section>

  <footer class="text-center py-6 border-t border-gray-800">
    <p class="text-gray-500">© 2025 VFX Crater. All rights reserved.</p>
  </footer>

</body>
</html>
