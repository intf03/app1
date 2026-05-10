import request from '@/utils/request'

// export function fetchUserData() {
//     return request.get('https://api.github.com/users/woai3c')
// }
import axios from 'axios'

const service = axios.create({
    baseURL:'http://127.0.0.1:8000/',
    timeout:40000,
})
export default service