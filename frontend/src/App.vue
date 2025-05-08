<template>
  <div id="app">
    <!-- Navigation -->
    <nav class="navbar fixed-top">
      <div class="navbar-content">
        <div class="logo">
          <h1>FilmTrack</h1>
        </div>
        <ul class="nav-links">
          <li><router-link to="/">Home</router-link></li>
          <li v-if="isAuthenticated">
            <router-link to="/movies">Movies</router-link>
          </li>
          <li v-if="isAdmin" class="admin-badge-nav">
    <span class="admin-badge">
      <i class="fas fa-shield-alt"></i> Admin
    </span>
  </li>
          <li v-if="!isAuthenticated">
            <router-link to="/login">Log In</router-link>
          </li>
          <li v-if="isAuthenticated">
            <a href="#" @click.prevent="logout" class="logout-link">
              <i class="fas fa-sign-out-alt"></i> Log Out
            </a>
          </li>
        </ul>
      </div>
    </nav>

    <!-- Dynamic content based on the route -->
    <div class="content-container">
      <router-view
        v-if="!isValidating"
        @login-success="handleLoginSuccess"
      ></router-view>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const token = ref(localStorage.getItem("access_token"));
const isValidating = ref(true);

//  handle role tracking
const userRole = ref(localStorage.getItem("user_role") || "BasicUser");

// Update the computed property for admin status
const isAdmin = computed(() => {
  return userRole.value === "AdminUser";
});

// Update the handleLoginSuccess method
const handleLoginSuccess = () => {
  console.log("Login success event received");
  token.value = localStorage.getItem("access_token");
  userRole.value = localStorage.getItem("user_role") || "BasicUser";
  console.log("User role from localStorage:", userRole.value);
};

// Computed property for authentication state
const isAuthenticated = computed(() => {
  console.log("isAuthenticated computed property, called token:", token.value);
  return !!token.value;
});

// Watch for token changes in localStorage
watch(
  () => localStorage.getItem("access_token"),
  (newToken) => {
    token.value = newToken;
    console.log("Token changed:", newToken ? "Token exists" : "No token");
  }
);

// Validate token with backend
async function validateToken() {
  isValidating.value = true;
  try {
    const storedToken = localStorage.getItem("access_token");
    if (!storedToken) {
      console.log("No token found in localStorage");
      token.value = null;
      throw new Error("No token");
    }

    console.log("Validating token with backend...");
    const response = await fetch("http://127.0.0.1:8000/users/validate-token", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${storedToken}`,
      },
    });

    if (response.ok) {
      console.log("Token validated successfully");
      token.value = storedToken;
    } else {
      console.log("Token validation failed:", response.status);
      token.value = null;
      throw new Error("Invalid token");
    }
  } catch (error) {
    console.error("Token validation error:", error.message);
    // Token is invalid or expired
    localStorage.removeItem("access_token");
    token.value = null;

    // Only redirect to login if user is trying to access a protected route
    if (router.currentRoute.value.meta?.requiresAuth) {
      console.log("Redirecting to login page");
      router.push("/login");
    }
  } finally {
    isValidating.value = false;
  }
}

// Update the logout function to clear role
async function logout() {
  console.log("Logging out...");
  try {
    // Invalidate token on backend
    await fetch("http://127.0.0.1:8000/users/logout", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token.value}`,
      },
    });
    console.log("Logout API call successful");
  } catch (error) {
    console.error("Logout API call failed:", error);
  } finally {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_role");
    token.value = null;
    userRole.value = "BasicUser";
    console.log("Redirecting to login page after logout");
    router.push("/login");
  }
}

// Check token on component mount
onMounted(() => {
  console.log("App component mounted");
  validateToken();
});
</script>

<style>
html,
body {
  height: 100%;
  width: 100%;
  margin: 0;
  overflow-x: hidden;
  font-family: sans-serif;
  background-color: #e5e5e5;
}
.admin-badge-nav {
  margin-right: auto; 
}

.admin-badge {
  background-color: #dc3545;
  color: white;
  padding: 3px 8px;
  border-radius: 5px;
  font-weight: bold;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.admin-badge i {
  font-size: 1rem;
}

#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.navbar {
  background-color: #5271ff;
  color: white;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  width: 100%;
  top: 0;
  z-index: 1000;
}

.navbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 0 1rem;
}

.logo h1 {
  color: white;
  margin: 0;
  font-size: 1.5rem;
}

.nav-links {
  display: flex;
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-links li {
  margin-left: 1.5rem;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-weight: bold;
  transition: color 0.3s ease;
  font-size: 1.1rem;
}

.nav-links a:hover {
  color: rgba(255, 255, 255, 0.8);
}

.nav-links a.router-link-active {
  text-decoration: underline;
}

.logout-link {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.logout-link i {
  margin-right: 5px;
}

.content-container {
  margin-top: 70px; /* Navbar height */
  padding: 20px;
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

@media (max-width: 768px) {
  .navbar-content {
    flex-direction: column;
    text-align: center;
    padding: 0.5rem;
  }

  .nav-links {
    flex-direction: row;
    justify-content: center;
    align-items: center;
    margin-top: 10px;
    flex-wrap: wrap;
  }

  .nav-links li {
    margin: 0.5rem 0.75rem;
  }

  .content-container {
    margin-top: 120px; /* Adjust for bigger navbar on mobile */
    padding: 15px;
  }
}
</style>
