// Game service
import axios from "axios";

import authHeader from "./auth-header";


// FIXME: hardcoded url
const API_URL = 'http://localhost:8888/api/v1/games/';

class GameService {
    getAll() {
        return axios.get(API_URL);
    }
    getDetails(name) {
        return axios.get(API_URL + name);
    }
    createRoom(game_id) {
        // FIXME: do we want to setup room size at creation
        return axios.post(API_URL+ game_id + "/rooms", null, {
            headers: authHeader()
        })
    }
    updateRoom(room_id) {
        console.log("update room")
    }
    getRoom(room_id) {
        return new Promise((resolve, reject) => {
            return ("room": {
                size: 2,
            });
        });
    }
}


export default new GameService();