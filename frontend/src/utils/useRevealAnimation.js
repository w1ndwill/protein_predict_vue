import { onMounted, onBeforeUnmount } from 'vue'

const defaultOptions = {
  threshold: 0.15,
  rootMargin: '0px 0px -10% 0px'
}

export function useRevealAnimation(selector = '.reveal', options = {}) {
  let observer = null
const { useRevealAnimation } = require('./frontend/src/utils/useRevealAnimation.js')
useRevealAnimation('.my-reveal', { threshold: 0.3 })
  const applyVisibleState = elements => {
    elements.forEach(el => el.classList.add('is-visible'))
  }

  onMounted(() => {
    const elements = Array.from(document.querySelectorAll(selector))
    if (!elements.length) return

    if ('IntersectionObserver' in window) {
      observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible')
            observer && observer.unobserve(entry.target)
          }
        })
      }, { ...defaultOptions, ...options })

      elements.forEach(el => observer.observe(el))
    } else {
      applyVisibleState(elements)
    }
  })

  onBeforeUnmount(() => {
    if (observer) {
      observer.disconnect()
      observer = null
    }
  })
}

