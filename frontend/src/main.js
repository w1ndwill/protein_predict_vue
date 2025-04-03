import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import { Upload } from '@element-plus/icons-vue'  // 添加这行
import 'element-plus/dist/index.css'
import 'bootstrap/dist/css/bootstrap.min.css'

const app = createApp(App)
app.component('Upload', Upload)  // 全局注册Upload组件
app.use(ElementPlus)
app.use(router)
app.mount('#app')