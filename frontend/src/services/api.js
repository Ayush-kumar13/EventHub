import React from 'react'
import axios from 'axios'

const api = axios.create({
    baseURL:"http://localhost:8000",
    headers:{
        "Content-Type":"application/json"
    }
})
api.interceptors.request.use(
    (config)=>{
        const access_token=localStorage.getItem("token")
        if (access_token){
            config.headers.Authorization=`Bearer ${access_token}`
        }
        return config
    },
    (error)=>{
        return Promise.reject(error)
    }
)


export default api
