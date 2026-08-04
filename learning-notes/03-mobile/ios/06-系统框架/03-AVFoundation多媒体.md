# AVFoundation 多媒体
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. AVAudioPlayer 音频播放

```swift
import AVFoundation

class AudioPlayerManager {
    private var audioPlayer: AVAudioPlayer?

    func playSound(named name: String) {
        guard let url = Bundle.main.url(forResource: name, withExtension: "mp3") else { return }
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .default)
            try AVAudioSession.sharedInstance().setActive(true)
            audioPlayer = try AVAudioPlayer(contentsOf: url)
            audioPlayer?.play()
        } catch {
            print("播放失败: \(error)")
        }
    }

    func pause() { audioPlayer?.pause() }
    func stop() { audioPlayer?.stop() }
    var isPlaying: Bool { audioPlayer?.isPlaying ?? false }
    var currentTime: TimeInterval { audioPlayer?.currentTime ?? 0 }
    var duration: TimeInterval { audioPlayer?.duration ?? 0 }
}
```

## 2. AVPlayer 视频播放

```swift
import AVKit

class VideoPlayerVC: UIViewController {
    private var player: AVPlayer?
    private var playerViewController: AVPlayerViewController?

    func playVideo(url: URL) {
        player = AVPlayer(url: url)
        playerViewController = AVPlayerViewController()
        playerViewController?.player = player

        if let playerVC = playerViewController {
            present(playerVC, animated: true) {
                self.player?.play()
            }
        }
    }

    // 内嵌播放器
    func embedPlayer(in containerView: UIView, url: URL) {
        player = AVPlayer(url: url)
        let playerLayer = AVPlayerLayer(player: player)
        playerLayer.frame = containerView.bounds
        playerLayer.videoGravity = .resizeAspectFill
        containerView.layer.addSublayer(playerLayer)
        player?.play()
    }
}
```

## 3. 播放进度监听

```swift
class PlayerObserver {
    private var player: AVPlayer
    private var timeObserver: Any?

    init(player: AVPlayer) {
        self.player = player
    }

    func startObserving(onProgress: @escaping (Double) -> Void) {
        let interval = CMTime(seconds: 0.5, preferredTimescale: CMTimeScale(NSEC_PER_SEC))
        timeObserver = player.addPeriodicTimeObserver(forInterval: interval, queue: .main) { time in
            let current = CMTimeGetSeconds(time)
            let duration = CMTimeGetSeconds(self.player.currentItem?.duration ?? .zero)
            if duration > 0 { onProgress(current / duration) }
        }
    }

    func stopObserving() {
        if let observer = timeObserver {
            player.removeTimeObserver(observer)
            timeObserver = nil
        }
    }
}
```

## 4. 相机拍照

```swift
import AVFoundation

class CameraManager: NSObject {
    private let captureSession = AVCaptureSession()
    private let photoOutput = AVCapturePhotoOutput()
    var onPhotoCaptured: ((UIImage) -> Void)?

    func setupCamera(in view: UIView) {
        captureSession.sessionPreset = .photo
        guard let camera = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back),
              let input = try? AVCaptureDeviceInput(device: camera) else { return }

        if captureSession.canAddInput(input) { captureSession.addInput(input) }
        if captureSession.canAddOutput(photoOutput) { captureSession.addOutput(photoOutput) }

        let previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
        previewLayer.frame = view.bounds
        previewLayer.videoGravity = .resizeAspectFill
        view.layer.addSublayer(previewLayer)

        DispatchQueue.global(qos: .userInitiated).async {
            self.captureSession.startRunning()
        }
    }

    func takePhoto() {
        let settings = AVCapturePhotoSettings()
        photoOutput.capturePhoto(with: settings, delegate: self)
    }
}

extension CameraManager: AVCapturePhotoCaptureDelegate {
    func photoOutput(_ output: AVCapturePhotoOutput,
                     didFinishProcessingPhoto photo: AVCapturePhoto, error: Error?) {
        guard let data = photo.fileDataRepresentation(),
              let image = UIImage(data: data) else { return }
        onPhotoCaptured?(image)
    }
}
```

## 5. 录音

```swift
class AudioRecorder {
    private var recorder: AVAudioRecorder?
    private let fileURL: URL

    init() {
        let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        fileURL = docs.appendingPathComponent("recording.m4a")
    }

    func startRecording() throws {
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 44100,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]
        try AVAudioSession.sharedInstance().setCategory(.record, mode: .default)
        recorder = try AVAudioRecorder(url: fileURL, settings: settings)
        recorder?.record()
    }

    func stopRecording() {
        recorder?.stop()
    }
}
```
