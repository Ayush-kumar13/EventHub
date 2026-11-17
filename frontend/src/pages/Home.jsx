import React from 'react'
import EventCard from '../components/EventCard'

const Home = () => {
  return (
    <div>
      <h1>Event hub Home page</h1>
      <h2>upcoming events</h2>
      <EventCard title="tech confrence 2026"
       description="Learn about latest technologies"
        location="Delhi"
        date="20 December 2026"
        price={500}/>
        
        <EventCard title="Music Festival"

                description="Enjoy live music performances"

                location="Noida"

                date="25 December 2026"

                price={1000}

            />
    </div>
  )
}

export default Home
