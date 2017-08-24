import Firebase from 'firebase'
import Firedux from 'firedux'
import { combineReducers } from 'redux'
import { webcastsById, specialWebcastIds } from './webcastsById'
import visibility from './visibility'
import videoGrid from './videoGrid'
import chats from './chats'
import favoriteTeams from './favorites'
import TBAAPIv3Firebase from '../tba_apiv3_firebase'

// Firebase
const firebaseApp = Firebase.initializeApp({
  apiKey: 'AIzaSyDBlFwtAgb2i7hMCQ5vBv44UEKVsA543hs',
  authDomain: 'tbatv-prod-hrd.firebaseapp.com',
  databaseURL: 'https://tbatv-prod-hrd.firebaseio.com',
})
const ref = firebaseApp.database().ref()
export const firedux = new Firedux({
  ref,
})

let fb = new TBAAPIv3Firebase(firebaseApp)
let ref2 = fb.getRef('v3/team/frc1');
console.log(ref2);
ref2.onUpdate((result) => {
  console.log(result)
  console.log("!!!!!!!!!!!")
})


const gamedayReducer = combineReducers({
  firedux: firedux.reducer(),
  webcastsById,
  specialWebcastIds,
  visibility,
  videoGrid,
  chats,
  favoriteTeams,
})

export default gamedayReducer
