import './assets/main.css'

import { createApp } from "vue";
import App from "./App.vue";
import router from "./router/router.js";  // Correct the path to the router.js file

createApp(App)
  .use(router)  // Use the router instance
  .mount("#app");

