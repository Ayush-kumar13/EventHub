import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { AuthProvider } from "./context/AuthContext";
import EventDetails from "./pages/EventDetails";
import Events from "./pages/Events";
import ProtectedRoute from "./components/ProtectedRoute";
import MyBookings from "./pages/MyBookings";
const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/events" element={<Events />} />
          <Route path="/events/:event_id" element={<EventDetails />} />
          <Route path="/my-bookings" element={<ProtectedRoute>
            <MyBookings/>
          </ProtectedRoute>}/>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
