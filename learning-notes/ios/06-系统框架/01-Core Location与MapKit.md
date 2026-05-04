# Core Location 与 MapKit
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 请求定位权限

```swift
import CoreLocation

class LocationManager: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
    }

    func requestPermission() {
        manager.requestWhenInUseAuthorization()  // 使用时定位
        // manager.requestAlwaysAuthorization()  // 始终定位
    }

    func startUpdating() {
        manager.startUpdatingLocation()
    }

    // 权限变化回调
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        switch manager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways:
            manager.startUpdatingLocation()
        case .denied, .restricted:
            print("定位权限被拒绝")
        case .notDetermined:
            requestPermission()
        @unknown default: break
        }
    }

    // 位置更新
    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last else { return }
        print("纬度: \(location.coordinate.latitude), 经度: \(location.coordinate.longitude)")
    }
}
```

## 2. 地理编码与反地理编码

```swift
let geocoder = CLGeocoder()

// 地址 → 坐标
func geocode(address: String) async throws -> CLLocationCoordinate2D? {
    let placemarks = try await geocoder.geocodeAddressString(address)
    return placemarks.first?.location?.coordinate
}

// 坐标 → 地址
func reverseGeocode(location: CLLocation) async throws -> String? {
    let placemarks = try await geocoder.reverseGeocodeLocation(location)
    guard let placemark = placemarks.first else { return nil }
    return [placemark.locality, placemark.subLocality, placemark.thoroughfare]
        .compactMap { $0 }
        .joined(separator: " ")
}
```

## 3. MKMapView 基础

```swift
import MapKit

class MapViewController: UIViewController {
    private let mapView = MKMapView()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.addSubview(mapView)
        mapView.frame = view.bounds
        mapView.delegate = self

        // 设置区域
        let center = CLLocationCoordinate2D(latitude: 39.9042, longitude: 116.4074)
        let region = MKCoordinateRegion(center: center,
                                         latitudinalMeters: 5000,
                                         longitudinalMeters: 5000)
        mapView.setRegion(region, animated: true)
        mapView.showsUserLocation = true
    }
}
```

## 4. 地图标注

```swift
// 添加标注
let annotation = MKPointAnnotation()
annotation.coordinate = CLLocationCoordinate2D(latitude: 39.9042, longitude: 116.4074)
annotation.title = "天安门"
annotation.subtitle = "北京市中心"
mapView.addAnnotation(annotation)

// 自定义标注视图
extension MapViewController: MKMapViewDelegate {
    func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
        guard !(annotation is MKUserLocation) else { return nil }
        let identifier = "CustomPin"
        var view = mapView.dequeueReusableAnnotationView(withIdentifier: identifier) as? MKMarkerAnnotationView
        if view == nil {
            view = MKMarkerAnnotationView(annotation: annotation, reuseIdentifier: identifier)
            view?.canShowCallout = true
            view?.markerTintColor = .systemRed
            view?.rightCalloutAccessoryView = UIButton(type: .detailDisclosure)
        }
        view?.annotation = annotation
        return view
    }
}
```

## 5. SwiftUI Map（iOS 17+）

```swift
import SwiftUI
import MapKit

struct MapContentView: View {
    @State private var position: MapCameraPosition = .region(
        MKCoordinateRegion(
            center: CLLocationCoordinate2D(latitude: 39.9042, longitude: 116.4074),
            span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
        )
    )

    var body: some View {
        Map(position: $position) {
            Marker("天安门", coordinate: CLLocationCoordinate2D(latitude: 39.9042, longitude: 116.4074))
            UserAnnotation()
        }
        .mapControls {
            MapUserLocationButton()
            MapCompass()
            MapScaleView()
        }
    }
}
```

## 6. iOS 26 MapKit 重大更新

<!-- version-check: MapKit iOS 26, PlaceDescriptor, MKReverseGeocodingRequest, Cycling Directions, checked 2026-05-04 -->

> 🔄 更新于 2026-05-04

iOS 26 对 MapKit 进行了多项重大更新，包括新的地点查找方式、地理编码 API 迁移、骑行导航和 Look Around 网页版。

来源：[WWDC25 Session 204: Go further with MapKit](https://developer.apple.com/videos/play/wwdc2025/204/)

### 6.1 PlaceDescriptor（GeoToolbox 框架）

新增 `PlaceDescriptor` 类型，允许在没有 Place ID 的情况下通过名称、地址或坐标查找地点的丰富数据：

```swift
import GeoToolbox
import MapKit

// 通过坐标查找地点
let descriptor = PlaceDescriptor(
    commonName: "Anna Livia Fountain",
    representations: [
        .coordinate(CLLocationCoordinate2D(latitude: 53.3498, longitude: -6.2603))
    ]
)

// 通过地址查找地点
let addressDescriptor = PlaceDescriptor(
    commonName: "Molly Malone Statue",
    representations: [
        .address("Suffolk Street, Dublin 2, Ireland")
    ]
)

// 使用 MKMapItemRequest 获取丰富的地点数据
let request = MKMapItemRequest(descriptor: descriptor)
let mapItem = try await request.mapItem

// mapItem 可用于所有 MapKit API（地图标注、Place Card 等）
```

**PlaceDescriptor 三种表示方式**：
- `.address(String)` — 邮寄地址
- `.coordinate(CLLocationCoordinate2D)` — 固定坐标点
- `.deviceLocation(CLLocation)` — GPS 设备位置（含精度、时间戳等）

### 6.2 地理编码迁移：CLGeocoder → MapKit

iOS 26 将地理编码从 CoreLocation 迁移到 MapKit，`CLGeocoder` 已被标记为废弃：

```swift
import MapKit

// 反向地理编码（坐标 → 地址）
let location = CLLocation(latitude: 39.9042, longitude: 116.4074)
let request = MKReverseGeocodingRequest(location: location)
let mapItems = try await request.mapItems
let mapItem = mapItems.first

// 多种地址显示格式
let fullAddress = mapItem?.address?.fullAddress       // 完整地址
let shortAddress = mapItem?.address?.shortAddress     // 简短地址
let city = mapItem?.addressRepresentations?.cityWithContext  // 城市+上下文

// 正向地理编码（地址 → 坐标）
let geoRequest = MKGeocodingRequest(address: "天安门广场, 北京")
let geoItems = try await geoRequest.mapItems
let coordinate = geoItems.first?.placemark.coordinate
```

**MKAddressRepresentations 提供的地址格式**：
- `fullAddress` — 完整邮政地址
- `shortAddress` — 关键部分
- `cityWithContext` — 城市 + 上下文（如"北京, 中国"或"洛杉矶, 加利福尼亚"）
- `fullAddress(includingRegion: Bool)` — 可选是否包含国家/地区

### 6.3 骑行导航（Cycling Directions）

MapKit 新增骑行导航支持，利用自行车道和步行道规划路线：

```swift
import MapKit

// 请求骑行导航
let directionsRequest = MKDirections.Request()
directionsRequest.source = MKMapItem.forCurrentLocation()
directionsRequest.destination = selectedMapItem
directionsRequest.transportType = .cycling  // 新增：骑行

let directions = MKDirections(request: directionsRequest)
let response = try await directions.calculate()

// 显示路线
if let route = response.routes.first {
    print("距离: \(route.distance / 1000) km")
    print("预计时间: \(route.expectedTravelTime / 60) 分钟")
    print("路线名称: \(route.name)")

    // 在 SwiftUI Map 上显示
    Map {
        MapPolyline(route.polyline)
            .stroke(.blue, lineWidth: 5)
    }
}
```

### 6.4 其他更新

- **watchOS MapKit 扩展**：20+ 个 MapKit API 首次登陆 Apple Watch，支持搜索、导航等
- **MapKit JS Look Around**：网页版支持 360° 街景浏览（交互式和预览两种模式）
- **统一 Maps URL**：iOS 18.4+ 更新了 Maps URL 格式，参数更一致、更易读
- **iOS 26.5 Maps 变化**：新增 Suggested Places 推荐功能，Apple Maps 将引入本地广告

来源：[9to5Mac iOS 26.5](https://9to5mac.com/2026/04/08/ios-26-5-new-iphone-features/)、[MacRumors iOS 26.5 Maps](https://www.macrumors.com/2026/04/18/ios-26-5-will-change-apple-maps-in-two-ways/)
