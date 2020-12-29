/*
*  Copyright (c) 2015 The WebRTC project authors. All Rights Reserved.
*
*  Use of this source code is governed by a BSD-style license
*  that can be found in the LICENSE file in the root of the source
*  tree.
*/

// This code is adapted from
// https://rawgit.com/Miguelao/demos/master/mediarecorder.html

'use strict';

/* globals MediaRecorder */
function startRecordProcedure() {
  $('#echoCancellation').bootstrapToggle();
  let mediaRecorder;
  let recordedBlobs;

  const gumVideo = document.querySelector('video#gum');
  const errorMsgElement = document.querySelector('span#errorMsg');
  const recordedVideo = document.querySelector('video#recorded');
  const recordButton = document.querySelector('button#record');
  const stopRecordButton = document.querySelector('button#stop-record');
  const pauseRecordButton = document.querySelector('button#pause-record');
  const resumeButton = document.querySelector('button#resume');
  const downloadButton = document.querySelector('button#download');
  const save_button = document.getElementById('save-record-button');

  recordedVideo.hidden = true;
  resumeButton.hidden = true;
  downloadButton.hidden = true;
  save_button.hidden = true;
  stopRecordButton.hidden = true;
  pauseRecordButton.hidden = true;

  save_button.onclick = function () {
    const blob = new Blob(recordedBlobs, {type: 'video/webm'});
    const event = new CustomEvent('save-record', {detail: blob});
    document.dispatchEvent(event);
  };
  recordButton.addEventListener('click', () => {
    startRecording();
  });
  pauseRecordButton.addEventListener('click', () => {
    mediaRecorder.pause();
    resumeButton.hidden = false;
    pauseRecordButton.hidden = true;
  });
  stopRecordButton.addEventListener('click', () => {
    stopRecording();
    stopRecordButton.hidden = true;
    resumeButton.hidden = true;
    save_button.hidden = false;
    downloadButton.hidden = false;
    recordButton.hidden = false;
    pauseRecordButton.hidden = true;

  });

  resumeButton.addEventListener('click', () => {
    mediaRecorder.resume();
    resumeButton.hidden = true;
    pauseRecordButton.hidden = false;
  });

  downloadButton.addEventListener('click', () => {
    const blob = new Blob(recordedBlobs, {type: 'video/webm'});
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = 'test.webm';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }, 100);
  });

  function handleDataAvailable(event) {
    console.log('handleDataAvailable', event);
    if (event.data && event.data.size > 0) {
      recordedBlobs.push(event.data);
    }
  }
  function handleStop(event){
    const superBuffer = new Blob(recordedBlobs, {type: 'video/webm'});
    recordedVideo.src = null;
    recordedVideo.srcObject = null;
    recordedVideo.src = window.URL.createObjectURL(superBuffer);
    recordedVideo.controls = true;
  }
  function startRecording() {
    gumVideo.hidden = false;
    recordedBlobs = [];
    let options = {mimeType: 'video/webm;codecs=vp9,opus'};
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
      console.error(`${options.mimeType} is not supported`);
      options = {mimeType: 'video/webm;codecs=vp8,opus'};
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        console.error(`${options.mimeType} is not supported`);
        options = {mimeType: 'video/webm'};
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
          console.error(`${options.mimeType} is not supported`);
          options = {mimeType: ''};
        }
      }
    }

    try {
      mediaRecorder = new MediaRecorder(window.stream, options);
    } catch (e) {
      console.error('Exception while creating MediaRecorder:', e);
      errorMsgElement.innerHTML = `Exception while creating MediaRecorder: ${JSON.stringify(e)}`;
      return;
    }

    console.log('Created MediaRecorder', mediaRecorder, 'with options', options);
    recordButton.hidden = true;
    stopRecordButton.hidden = false;
    pauseRecordButton.hidden = false;
    resumeButton.hidden = true;
    downloadButton.hidden = true;
    mediaRecorder.onstop = (event) => {
      console.log('Recorder stopped: ', event);
      console.log('Recorded Blobs: ', recordedBlobs);
    };
    mediaRecorder.ondataavailable = handleDataAvailable;
    mediaRecorder.onstop = handleStop;
    mediaRecorder.start();
    console.log('MediaRecorder started', mediaRecorder);
  }

  function stopRecording() {
    mediaRecorder.stop();
    recordedVideo.hidden = false;
    gumVideo.hidden = true;
  }

  function handleSuccess(stream) {
    recordButton.disabled = false;
    console.log('getUserMedia() got stream:', stream);
    window.stream = stream;

    gumVideo.srcObject = stream;
  }

  async function init(constraints) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      handleSuccess(stream);
    } catch (e) {
      console.error('navigator.getUserMedia error:', e);
      errorMsgElement.innerHTML = `navigator.getUserMedia error:${e.toString()}`;
    }
  }

  document.addEventListener( 'DOMContentLoaded',  async function () {
    const hasEchoCancellation = document.querySelector('#echoCancellation').checked;
    const constraints = {
      audio: {
        echoCancellation: {exact: hasEchoCancellation}
      },
      video: {
        width: 1280, height: 720
      }
    };
    console.log('Using media constraints:', constraints);
    await init(constraints);
  }());
}
