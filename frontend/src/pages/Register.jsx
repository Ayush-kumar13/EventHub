import React, { useState } from 'react'

const Register = () => {
    const [name,setName]=useState("")
    const [email,setEmail]=useState('')
    const [password,setPassword]=useState('')
    const handleSubmit=(event)=>{
        event.preventDefault()
        if ( !name || !email || !password ) {
            alert("All fields are required ")
            return
        }
    }
  return (
    <div>
      <form onSubmit={handleSubmit}>
        
        <input type='text' placeholder='enter name' value={name} onChange={(event)=>{setName(event.target.value)}}/>

        <input type='email ' placeholder='enter email' value={email}  onChange={(event)=>{setEmail(event.target.value)}}/>

        <input type='password' placeholder='enter pass' value={password}  onChange={(event)=>{setPassword(event.target.value)}}/>

        <button type='submit' >Register</button>

      </form>

    </div>
  )
}

export default Register
