import React,{createContext, useContext, useEffect, useState} from "react";
import api from "../services/api";
const AuthContext=createContext()

export const AuthProvider=({children})=>{

    const [user,setUser]=useState(null)


    const [token,setToken]=useState(
        localStorage.getItem("token")

    )
    const [loading, setLoading] = useState(true);

    const login=(userData,access_token)=>{
        localStorage.setItem("token",access_token)

        setToken(access_token)
        setUser(userData)

    }
    const logout=()=>{
        localStorage.removeItem("token")
        setToken(null)
        setUser(null)
    }
    useEffect(()=>
        {
            const checkUser=async()=>{

            if(!token){
            setLoading(false);
            return
        }
        try{
            const response= await api.get('/me',{headers:{
                Authorization:`Bearer ${token}`
            }})
            setUser(response.data)

            } 
         catch(error){
            console.log("Authentication failed",error.response?.data)

            localStorage.removeItem("token")
            setToken(null);
            setUser(null);
        }
        finally{
            setLoading(false);
        }



    };
    checkUser();
    },[])
    return(
        <AuthContext.Provider value={{user,token,login,logout,setUser,loading}}>
        {children}
        </AuthContext.Provider>
    )

}
export const useAuth=()=>{
    return useContext(AuthContext)
}
