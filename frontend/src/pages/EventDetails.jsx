import React from 'react'
import {useParams} from 'react-router-dom'
const EventDetails = () => {
    const {event_id}=useParams()
  return (
    <div>
      <h1>EventDetails</h1>
      <p>Event Id : {event_id}
      </p>
    </div>
  )
}

export default EventDetails
