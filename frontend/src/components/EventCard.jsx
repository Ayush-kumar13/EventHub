import React from 'react'
import { Link } from 'react-router-dom'

const EventCard = (props) => {
  return (
    <div>
        <hr/>
        <h2>{props.title}</h2>
        <p>{props.description}</p>
        <p>Location:{props.location}</p>
        <p>Price:{props.price}</p>
        <Link to ={`/events/${props.event_id}`}>
        View Details 
        </Link>
        <hr/>
      
    </div>
  )
}

export default EventCard
