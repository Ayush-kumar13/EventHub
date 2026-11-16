import React from 'react'
import { Link } from 'react-router-dom'

const Navbar = () => {
  return (
    <nav>
        <h2>EventHub NAVBAR</h2>
        <div className="">
            <Link to='/'>Home</Link>
            <Link to ='/events'>Events</Link>
            <Link to ="/login">Login</Link>
            <Link to ='/register'>Register</Link>
        </div>
      
    </nav>
  )
}

export default Navbar
