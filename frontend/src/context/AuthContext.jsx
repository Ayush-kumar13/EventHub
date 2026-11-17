import React,{createContext, useContext, useState} from "react";
const AuthContext=createContext()

export const AuthProvider=({children})=>{

    const [user,setUser]=useState(null)


    const [token,setToken]=useState(
        localStorage.getItem("token")

    )
    const login=(userData,access_Token)=>{
        localStorage.setItem("token",access_Token)

        setToken(access_Token)
        setUser(userData)

    }
    const logout=()=>{
        localStorage.removeItem("token")
        setToken(null)
        setUser(null)
    }
    return(
        <AuthContext.Provider value={{user,token,login,logout,setUser}}>
        {children}
        </AuthContext.Provider>
    )

}
export const useAuth=()=>{
    return useContext(AuthContext)
}