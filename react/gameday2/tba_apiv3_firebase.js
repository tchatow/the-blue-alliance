import Firebase from 'firebase'


class APIRef {
  constructor(firebaseApp, uri) {
    this.firebaseRef = firebaseApp.database().ref(`api_updated/${uri}/_hash`)
    this.uri = uri
  }

  onUpdate(callback) {
    this.firebaseRef.on('value', (snapshot) => {
      fetch(`/api/${this.uri}?hash=${snapshot.val()}`, {
        headers: {'X-TBA-Auth-Key': 'BjEM7kValdmFNZANYbSMsnpY26mjYn5mdderI3XoYT3Sdv2uNBex8nm0EdQkQIqj'},
      }).then((response) => {
        if (response.status === 200) {
          return response.json()
        }
        return null
      }).then((result) => {
        callback(result)
      })
    })
  }

  disconnect() {
    this.firebaseRef.off('value')
  }
}


class TBAAPIv3Firebase {
  constructor(firebaseApp) {
    this.firebaseApp = firebaseApp
  }

  getRef(uri) {
    return new APIRef(this.firebaseApp, uri)
  }
}

export default TBAAPIv3Firebase
