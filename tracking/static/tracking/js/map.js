let myLat = null, myLng = null

document.addEventListener('DOMContentLoaded', function () {
    const map = L.map('mapid', {
        center: [10.762622, 106.660172],
        zoom: 13,
        fullscreenControl: true,
        fullscreenControlOptions: {
            position: 'topleft',
            title: "Fullscreen",
            titleCancel: "Exit Fullscreen"
        }
    })
    let routeLayer = null

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors'
    }).addTo(map)

    const userIsLoggedIn = USER_IS_LOGGED_IN

    if (userIsLoggedIn) {
        fetch('/api/get_all_locations/')
            .then((response) => {
                if (!response.ok) throw new Error('Không thể lấy dữ liệu')
                return response.json()
            })
            .then((data) => {
                data.forEach((loc) => {
                    const marker = L.marker([loc.latitude, loc.longitude]).addTo(map)
                    marker.bindPopup(`
              <b>${loc.user}</b><br>${loc.timestamp}<br>
              <button class="btn btn-sm btn-primary mt-2 route-btn"
                      data-lat="${loc.latitude}" data-lng="${loc.longitude}">
                Tìm đường đi
              </button>
            `)
                })
            })
            .catch((err) => {
                console.error(err)
                alert('Lỗi khi lấy dữ liệu bản đồ.')
            })
    }

    document.getElementById('btnSearch').addEventListener('click', function () {
        if (!userIsLoggedIn) {
            window.location.href = '/login/'
            return
        }

        const username = document.getElementById('searchUser').value.trim()
        if (!username) {
            alert('Vui lòng nhập tên người dùng.')
            return
        }

        fetch(`/api/get_user_location/${username}/`)
            .then((response) => {
                if (!response.ok) throw new Error('Không tìm thấy người dùng hoặc chưa có vị trí.')
                return response.json()
            })
            .then((loc) => {
                const { latitude, longitude, timestamp } = loc

                const marker = L.marker([latitude, longitude], {
                    icon: L.icon({
                        iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
                        iconSize: [30, 48],
                        iconAnchor: [15, 48],
                        popupAnchor: [0, -40]
                    })
                }).addTo(map)

                marker.bindPopup(`
            <b>${username}</b><br>${timestamp}<br>
            <button class="btn btn-sm btn-primary mt-2 route-btn"
                    data-lat="${latitude}" data-lng="${longitude}">
              Tìm đường đi
            </button>
          `).openPopup()

                map.setView([latitude, longitude], 16)
            })
            .catch((error) => {
                alert(error.message)
            })
    })

    map.on('popupopen', function (e) {
        const button = e.popup._contentNode.querySelector('.route-btn')
        if (button) {
            button.addEventListener('click', function () {
                const destLat = parseFloat(button.getAttribute('data-lat'))
                const destLng = parseFloat(button.getAttribute('data-lng'))

                if (!myLat || !myLng) {
                    console.log('myLat:', myLat, 'myLng:', myLng)
                    alert('Không xác định được vị trí hiện tại.')
                    return
                }

                fetch('https://api.openrouteservice.org/v2/directions/driving-car?geometry_format=geojson', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': '5b3ce3597851110001cf6248a7b5720432d146eb922049918ffd2d20'
                    },
                    body: JSON.stringify({
                        coordinates: [[myLng, myLat], [destLng, destLat]],
                    })
                })
                    .then((res) => res.json())
                    .then((data) => {
                        console.log('Dữ liệu định tuyến trả về:', data)
                      
                        if (!data || !data.routes || data.routes.length === 0) {
                          alert('Không thể tìm đường đi (không có dữ liệu định tuyến).')
                          return
                        }
                      
                        const encoded = data.routes[0].geometry
                        const coords = polyline.decode(encoded)
                      
                        if (routeLayer) {
                          map.removeLayer(routeLayer)
                        }
                      
                        routeLayer = L.polyline(coords, { color: 'blue', weight: 4 }).addTo(map)
                        map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] })

                        const distanceMeters = data.routes[0].summary.distance
                        const durationSeconds = data.routes[0].summary.duration

                        const distanceKm = (distanceMeters / 1000).toFixed(2)
                        const durationMin = Math.ceil(durationSeconds / 60)

                        const midIndex = Math.floor(coords.length / 2)
                        const midPoint = coords[midIndex]
                       
                        L.popup()
                        .setLatLng(midPoint)
                        .setContent(`<b>📍 ${distanceKm} km<br>🕒 ${durationMin} phút</b>`)
                        .openOn(map)                        
                    })
                    .catch((err) => {
                        console.error('Lỗi khi tìm đường:', err)
                        alert('Không thể tìm đường đi.')
                    })
            })
        }
    })

    updateUserLocation()
    setInterval(updateUserLocation, 10000)
    
})

function updateUserLocation() {
    if (!navigator.geolocation) {
        alert('Trình duyệt của bạn không hỗ trợ định vị.')
        return
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const { latitude, longitude } = position.coords

            myLat = latitude
            myLng = longitude
            console.log('Đã định vị:', myLat, myLng)

            fetch('/api/update_location/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ latitude, longitude })
            })
                .then((response) => {
                    if (!response.ok) throw new Error('Không thể cập nhật vị trí.')
                    console.log('Đã gửi vị trí:', latitude, longitude)
                })
                .catch((err) => {
                    console.error('Lỗi khi gửi vị trí:', err)
                })
        },
        (error) => {
            console.error('Lỗi lấy vị trí:', error)
        }
    )
}

function getCSRFToken() {
    const name = 'csrftoken'
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim()
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1))
        }
    }
    return ''
}


