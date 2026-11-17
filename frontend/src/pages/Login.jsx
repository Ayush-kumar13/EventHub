import React, { useState } from 'react'
import api from '../services/api'
const Login = () => {
    const[email,setEmail]=useState('')

    const[password,setPassword]=useState(" ")

    const handleLogin=async (event)=>{
      event.preventDefault()
      try{
        const response=await api.post('/login',{
          email:email,password:password
        })
        console.log(response.data)

        localStorage.setItem("token",response.data.access_token)


      }

      catch(error){
        console.log(error.response?.data)
      }

    }
  return (
    <div>
        <h1>Login page</h1>

        <input type='email' placeholder='Enter your email address' value={email} onChange={(event)=>{setEmail(event.target.value)}}/>

        <input type="password" placeholder='Enter password'
        value={password}
        onChange={(event)=>{setPassword(event.target.value)}}/>

        <button type='submit' onClick={handleLogin}>Login </button>
    </div>
  )
}

export default Login
