import React from 'react'
import {Navigate}from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
const ProtectedRoute = ({children}) => {
    const{user,token}=useAuth()
    if (!token||!user){
        return<Navigate to ='/login' replace/>
    }
  return (
    children
  )
}

export default ProtectedRoute
