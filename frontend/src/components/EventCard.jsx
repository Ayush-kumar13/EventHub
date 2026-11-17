import React from 'react'

const EventCard = (props) => {
  return (
    <div>
        <hr/>
        <h2>{props.title}</h2>
        <p>{props.description}</p>
        <p>Location:{props.location}</p>
        <p>Price:{props.price}</p>
        <button>View Details</button>
        <hr/>
      
    </div>
  )
}

export default EventCard
