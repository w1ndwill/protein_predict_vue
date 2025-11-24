<template>
  <div class="particles-container">
    <Particles
      id="tsparticles"
      :particlesInit="particlesInit"
      :options="particleOptions"
    />
  </div>
</template>

<script>
import { loadFull } from "tsparticles"; 

export default {
  name: 'ParticlesBackground',
  data() {
    return {
      // Particle.js Configuration Options
      particleOptions: {
        background: {
          color: {
            value: 'transparent' // The background will be handled by the parent
          }
        },
        fpsLimit: 60,
        interactivity: {
          events: {
            onHover: {
              enable: true,
              mode: 'repulse' // Makes particles move away from the cursor
            },
            onClick: {
              enable: true,
              mode: 'push' // Adds new particles on click
            }
          },
          modes: {
            repulse: {
              distance: 100,
              duration: 0.4
            },
            push: {
              quantity: 4
            }
          }
        },
        particles: {
          color: {
            value: '#adb5bd' // A subtle grey, matching our light theme's border color
          },
          links: {
            color: '#ced4da', // A slightly lighter grey for the links
            distance: 150,
            enable: true,
            opacity: 0.4,
            width: 1
          },
          collisions: {
            enable: true
          },
          move: {
            direction: 'none',
            enable: true,
            outModes: {
              default: 'bounce'
            },
            random: false,
            speed: 1, // A slow, calming speed
            straight: false
          },
          number: {
            density: {
              enable: true,
              area: 800
            },
            value: 80 // Adjust particle count here
          },
          opacity: {
            value: 0.5
          },
          shape: {
            type: 'circle'
          },
          size: {
            value: { min: 1, max: 3 } // Small, subtle particles
          }
        },
        detectRetina: true
      }
    };
  },
  methods: {
    async particlesInit(engine) {
      // Initializes the tsparticles engine
      await loadFull(engine);
    }
  }
};
</script>

<style scoped>
.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0; /* Ensure it's behind the content */
}
</style>
