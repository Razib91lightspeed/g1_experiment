#include <iostream>
#include <thread>
#include <chrono>

#include <unitree/robot/channel/channel_factory.hpp>
#include <unitree/robot/g1/audio/g1_audio_client.hpp>

int main() {
    std::cout << "Connecting to G1 audio service..." << std::endl;

    unitree::robot::ChannelFactory::Instance()->Init(
        0, "eth0"
    );

    unitree::robot::g1::AudioClient audio;

    audio.Init();
    audio.SetTimeout(10.0f);

    uint8_t volume = 0;
    int ret = audio.GetVolume(volume);

    std::cout << "GetVolume result: " << ret << std::endl;

    if (ret == 0) {
        std::cout << "Current volume: "
                  << static_cast<int>(volume) << std::endl;

        if (volume < 50) {
            ret = audio.SetVolume(60);
            std::cout << "SetVolume result: " << ret << std::endl;
        }
    }

    std::cout << "G1, say: Hello, I am Raapple, and I am a new employee of FieldLab. I am from Tampere University of Applied Sciences." << std::endl;

    ret = audio.TtsMaker("Hello, I am Raapple, and I am a new employee of FieldLab. I am from Tampere University of Applied Sciences. I can see a chair in front of me.", 1);

    std::cout << "TtsMaker result: " << ret << std::endl;

    if (ret != 0) {
        std::cerr << "Speech request failed." << std::endl;
        return 1;
    }

    // Keep the client alive briefly for playback.
    std::this_thread::sleep_for(std::chrono::seconds(5));

    std::cout << "Speech request completed." << std::endl;

    return 0;
}
