<template>
  <div class="auth-page">
    <div class="tabs">
      <button 
        :class="{ active: mode==='login' }" 
        @click="mode = 'login'"
      >
        Log In
      </button>
      <button 
        :class="{ active: mode==='signup' }" 
        @click="mode = 'signup'"
      >
        Sign Up
      </button>
    </div>

    <form v-if="mode==='login'" @submit.prevent="submitLogin" class="form">
      <h2>Log In</h2>
      <div class="field">
        <label>Username</label>
        <input v-model="loginUsername" required />
      </div>
      <div class="field">
        <label>Password</label>
        <input v-model="loginPassword" type="password" required />
      </div>
      <button type="submit">Log In</button>
      <p v-if="loginError" class="error">{{ loginError }}</p>
    </form>

    <form v-else @submit.prevent="submitSignup" class="form">
      <h2>Sign Up</h2>
      <div class="field">
        <label>Username</label>
        <input v-model="signupUsername" required />
      </div>
      <div class="field">
        <label>Email</label>
        <input v-model="signupEmail" type="email" required />
      </div>
      <div class="field">
        <label>Password</label>
        <input v-model="signupPassword" type="password" required />
      </div>
      <button type="submit">Sign Up</button>
      <p v-if="signupError" class="error">{{ signupError }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router   = useRouter()
const apiBase  = 'http://127.0.0.1:8000'
const mode     = ref('login')     // 'login' or 'signup'

// login state
const loginUsername = ref('')
const loginPassword = ref('')
const loginError    = ref('')

// signup state
const signupUsername = ref('')
const signupEmail    = ref('')
const signupPassword = ref('')
const signupError    = ref('')

// LOG IN
async function submitLogin() {
  loginError.value = ''
  try {
    const form = new URLSearchParams()
    form.append('username', loginUsername.value)
    form.append('password', loginPassword.value)

    const res = await fetch(`${apiBase}/users/sign-in`, {
      method: 'POST',
      headers: { 'Content-Type':'application/x-www-form-urlencoded' },
      body: form.toString()
    })
    const data = await res.json()
    if (res.ok && data.access_token) {
      localStorage.setItem('access_token', data.access_token)
      router.push('/movies')
    } else {
      loginError.value = data.detail || 'Invalid credentials'
    }
  } catch {
    loginError.value = 'Network error'
  }
}

// SIGN UP
async function submitSignup() {
  signupError.value = ''
  try {
    const res = await fetch(`${apiBase}/users/signup`, {
      method: 'POST',
      headers: { 'Content-Type':'application/json' },
      body: JSON.stringify({
        username: signupUsername.value,
        email:    signupEmail.value,
        password: signupPassword.value
      })
    })
    const data = await res.json()
    if (res.ok && data.message) {
      // after signup, switch to login mode
      mode.value = 'login'
    } else {
      signupError.value = data.detail || 'Signup failed'
    }
  } catch {
    signupError.value = 'Network error'
  }
}
</script>

<style scoped>
.auth-page {
  max-width: 360px;
  margin: 4rem auto;
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.tabs {
  display: flex;
  margin-bottom: 1.5rem;
}
.tabs button {
  flex: 1;
  padding: 0.75rem;
  border: none;
  background: #f0f0f0;
  cursor: pointer;
}
.tabs button.active {
  background: #5271ff;
  color: white;
}
.form .field {
  margin-bottom: 1rem;
}
.form label {
  display: block;
  margin-bottom: 0.25rem;
}
.form input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.form button {
  width: 100%;
  padding: 0.6rem;
  background: #5271ff;
  color: white;
  border: none;
  border-radius: 4px;
}
.error {
  color: #d93025;
  margin-top: 0.75rem;
}
</style>
