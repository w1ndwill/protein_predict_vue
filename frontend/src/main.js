import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import Particles from "@tsparticles/vue3";
import { loadFull } from "tsparticles"; 
import { Upload } from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import 'bootstrap/dist/css/bootstrap.min.css'
import './assets/styles/theme.css'

const app = createApp(App)

app.use(Particles, {
  init: async engine => {
    await loadFull(engine);
  },
});

app.component('Upload', Upload)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
