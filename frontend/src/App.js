import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [textModel, setTextModel] = useState('gpt-4o-mini');
  const [audioModel, setAudioModel] = useState('tts-1');
  const [speaker1Voice, setSpeaker1Voice] = useState('alloy');
  const [speaker2Voice, setSpeaker2Voice] = useState('echo');
  const [useFishAudio, setUseFishAudio] = useState(false);
  const [fishSpeaker1, setFishSpeaker1] = useState('zhou');
  const [fishSpeaker2, setFishSpeaker2] = useState('dong');
  const [transcript, setTranscript] = useState('');
  const [audioFile, setAudioFile] = useState('');
  const [status, setStatus] = useState('');
  const [uploadStatus, setUploadStatus] = useState('');
  const [progress, setProgress] = useState(0);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setUploadStatus('文件已选择：' + event.target.files[0].name);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setStatus('正在处理...');
    setProgress(0);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('text_model', textModel);
    formData.append('audio_model', audioModel);
    formData.append('speaker_1_voice', speaker1Voice);
    formData.append('speaker_2_voice', speaker2Voice);
    formData.append('use_fish_audio', useFishAudio);
    formData.append('fish_speaker_1', fishSpeaker1);
    formData.append('fish_speaker_2', fishSpeaker2);

    try {
      const response = await axios.post('http://localhost:5000/api/convert', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        }
      });
      setTranscript(response.data.transcript);
      setAudioFile(response.data.audio_file);
      setStatus('转换完成');
    } catch (error) {
      setStatus('转换失败: ' + (error.response?.data?.error || error.message));
      console.error('Error details:', error.response?.data?.traceback || error);
    }
  };

  return (
    <div className="min-h-screen bg-durian-light">
      <div className="container mx-auto px-4 py-8 max-w-3xl">
        <h1 className="text-5xl font-bold text-center mb-12 text-durian-accent drop-shadow-lg hover:scale-105 transition-transform duration-300">榴莲猫播客</h1>
        <form onSubmit={handleSubmit} className="space-y-6 bg-durian-medium p-8 rounded-lg shadow-lg hover:shadow-2xl transition-shadow duration-300">
          <div>
            <label htmlFor="file-upload" className="block text-lg font-medium mb-2 text-durian-accent">
              上传PDF文件：
            </label>
            <input
              id="file-upload"
              type="file"
              onChange={handleFileChange}
              accept=".pdf"
              required
              className="w-full px-4 py-3 border-2 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-opacity-50 focus:border-durian-accent transition-all duration-300 hover:border-durian-accent"
              style={{ borderColor: '#FFBB70' }}
            />
            {uploadStatus && <p className="mt-2 text-sm text-durian-accent">{uploadStatus}</p>}
          </div>
          
          <div>
            <label htmlFor="text-model" className="block text-sm font-medium text-gray-700 mb-2">
              选择文本生成模型：
            </label>
            <select
              id="text-model"
              value={textModel}
              onChange={(e) => setTextModel(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="gpt-4o-mini">gpt-4o-mini</option>
              <option value="gpt-4o">gpt-4o</option>
              <option value="o1-preview">o1-preview</option>
              <option value="o1-mini">o1-mini</option>
            </select>
          </div>

          <div>
            <label htmlFor="audio-model" className="block text-sm font-medium text-gray-700 mb-2">
              选择音频生成模型：
            </label>
            <select
              id="audio-model"
              value={audioModel}
              onChange={(e) => setAudioModel(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="tts-1">tts-1</option>
              <option value="tts-1-hd">tts-1-hd</option>
            </select>
          </div>

          <div className="flex items-center">
            <input
              id="use-fish-audio"
              type="checkbox"
              checked={useFishAudio}
              onChange={(e) => setUseFishAudio(e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="use-fish-audio" className="ml-2 block text-sm text-gray-900">
              使用Fish Audio API
            </label>
          </div>

          {!useFishAudio && (
            <>
              <div>
                <label htmlFor="speaker1-voice" className="block text-sm font-medium text-gray-700 mb-2">
                  选择说话者1的声音：
                </label>
                <select
                  id="speaker1-voice"
                  value={speaker1Voice}
                  onChange={(e) => setSpeaker1Voice(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="alloy">alloy</option>
                  <option value="echo">echo</option>
                  <option value="fable">fable</option>
                  <option value="onyx">onyx</option>
                  <option value="nova">nova</option>
                  <option value="shimmer">shimmer</option>
                </select>
              </div>

              <div>
                <label htmlFor="speaker2-voice" className="block text-sm font-medium text-gray-700 mb-2">
                  选择说话者2的声音：
                </label>
                <select
                  id="speaker2-voice"
                  value={speaker2Voice}
                  onChange={(e) => setSpeaker2Voice(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="alloy">alloy</option>
                  <option value="echo">echo</option>
                  <option value="fable">fable</option>
                  <option value="onyx">onyx</option>
                  <option value="nova">nova</option>
                  <option value="shimmer">shimmer</option>
                </select>
              </div>
            </>
          )}

          {useFishAudio && (
            <>
              <div>
                <label htmlFor="fish-speaker1" className="block text-sm font-medium text-gray-700 mb-2">
                  选择说话者1的声音（Fish Audio）：
                </label>
                <select
                  id="fish-speaker1"
                  value={fishSpeaker1}
                  onChange={(e) => setFishSpeaker1(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="zhou">周（Zhou）</option>
                  <option value="dong">东（Dong）</option>
                  <option value="xing">星（Xing）</option>
                  <option value="yang">杨（Yang）</option>
                  <option value="新种子名">新种子的显示名称</option>  {/* 在这里添加新的选项 */}
                </select>
              </div>

              <div>
                <label htmlFor="fish-speaker2" className="block text-sm font-medium text-gray-700 mb-2">
                  选择说话者2的声音（Fish Audio）：
                </label>
                <select
                  id="fish-speaker2"
                  value={fishSpeaker2}
                  onChange={(e) => setFishSpeaker2(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="zhou">周（Zhou）</option>
                  <option value="dong">东（Dong）</option>
                  <option value="xing">星（Xing）</option>
                  <option value="yang">杨（Yang）</option>
                  <option value="新种子名">新种子的显示名称</option>  {/* 在这里也添加新的选项 */}
                </select>
              </div>
            </>
          )}

          <button
            type="submit"
            className="w-full px-6 py-3 font-semibold rounded-md shadow-md text-white bg-durian-accent hover:bg-durian-dark hover:scale-105 transition-all duration-300"
          >
            转换PDF
          </button>
        </form>

        <div className="mt-6 text-center font-semibold">{status}</div>
        {progress > 0 && progress < 100 && (
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
              <div className="bg-blue-600 h-2.5 rounded-full" style={{width: `${progress}%`}}></div>
            </div>
            <p className="text-center mt-2">{progress}% 完成</p>
          </div>
        )}

        {transcript && (
          <div className="mt-12 bg-durian-medium p-8 rounded-lg shadow-lg hover:shadow-2xl transition-all duration-300">
            <h2 className="text-2xl font-semibold mb-4 text-durian-accent">生成的文本记录：</h2>
            <textarea
              value={transcript}
              readOnly
              rows="10"
              className="w-full px-4 py-3 border-2 rounded-md shadow-inner focus:outline-none focus:ring-2 focus:ring-opacity-50 transition-all duration-300"
              style={{ borderColor: '#FFBB70', backgroundColor: '#FFFBDA', color: '#ED9455' }}
            />
          </div>
        )}

        {audioFile && (
          <div className="mt-12 bg-durian-medium p-8 rounded-lg shadow-lg hover:shadow-2xl transition-all duration-300">
            <h2 className="text-2xl font-semibold mb-4 text-durian-accent">生成的音频：</h2>
            <audio
              controls
              src={`http://localhost:5000/api/download?file=${audioFile}`}
              className="w-full mb-4"
            />
            <a
              href={`http://localhost:5000/api/download?file=${audioFile}`}
              download
              className="inline-block px-6 py-3 text-white font-semibold rounded-md shadow-md bg-durian-accent hover:bg-durian-dark hover:scale-105 transition-all duration-300"
            >
              下载音频文件
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;