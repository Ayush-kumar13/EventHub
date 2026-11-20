import React, { useState } from 'react'
import api from '../services/api'
import { useAuth } from '../context/AuthContext'

const Login = () => {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')

    const { login } = useAuth()

    const handleLogin = async (event) => {
        event.preventDefault()

        try {
            const response = await api.post('/login', {
                email: email,
                password: password
            })

            console.log("Login successful:", response.data)

            const access_token = response.data.access_token

            const user_response = await api.get('/me', {
                headers: {
                    Authorization: `Bearer ${access_token}`
                }
            })

            console.log("User data:", user_response.data)

            login(user_response.data, access_token)

        }
        catch (error) {
            console.log("Login error:", error.response?.data)
        }
    }

    return (
        <div>
            <h1>Login page</h1>

            <form onSubmit={handleLogin}>
                <input
                    type="email"
                    placeholder="Enter your email address"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                />

                <input
                    type="password"
                    placeholder="Enter password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                />

                <button type="submit">Login</button>
            </form>
        </div>
    )
}

export default Login