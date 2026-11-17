import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const Navbar = () => {
  const{user,logout}=useAuth()
  return (
    <nav>
        <h2>EventHub NAVBAR</h2>
        <div className="">
            <Link to='/'>Home</Link>
            <Link to ='/events'>Events</Link>

            {!user &&(<>
            <Link to ="/login">Login</Link>
            <Link to ='/register'>Register</Link>
            </>)}
            
            {user && <>
            <span>Welcome,{user.name} </span>

            <button onClick={logout}>
              Logout
              </button>
            </>}
            
        </div>
      
    </nav>
  )
}

export default Navbar
