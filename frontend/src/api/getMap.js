import axios from 'axios'
export default function getMap() {
   return axios.get('/map/china.json') 
}