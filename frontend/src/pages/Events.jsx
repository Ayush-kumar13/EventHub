import React, { useState, useEffect } from 'react'
import api from '../services/api'

const Events = () => {

    const [events, setEvents] = useState([])

    const [loading, setLoading] = useState(false)

    const [error, setError] = useState("")

    const getEvents = async () => {

        try {

            setLoading(true)

            const response = await api.get('/events')

            setEvents(response.data.events)

        } catch (error) {

            setError("Failed to load events")

            console.log(error)

        } finally {

            setLoading(false)

        }

    }

    useEffect(() => {

        getEvents()

    }, [])

    return (

        <div>

            <h1>All Events</h1>

            {loading && <p>Loading events...</p>}

            {error && <p>{error}</p>}

            {events.map((event) => (

                <div key={event.id}>

                    <h2>{event.title}</h2>

                    <p>{event.description}</p>

                    <p>{event.location}</p>

                    <p>Price: ₹{event.price}</p>

                </div>

            ))}

        </div>

    )

}

export default Events