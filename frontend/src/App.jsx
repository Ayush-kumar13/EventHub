import React from 'react'
import{BrowserRouter ,Routes,Route} from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Counter from './pages/Counter'
import Events from './pages/Events'
const App = () => {
  return (
    <BrowserRouter>
    <Navbar/>

    <Routes>
      <Route path="/" element={<Home/>}/>
      <Route path="/login" element={<Login/>}/>
      <Route path="/register" element={<Register/>}/>
      <Route path ="/events" element={<Events/>}/>
     </Routes>

    </BrowserRouter>
  )
}

export default App
