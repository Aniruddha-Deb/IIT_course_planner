import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'

import { VueDragula } from 'vue3-dragula'
import 'dragula/dist/dragula.min.css'

const vueApp = createApp(App);

vueApp.use(VueDragula);

vueApp.mount('#app')
