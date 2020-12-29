/*
 *  Copyright (c) 2015 The WebRTC project authors. All Rights Reserved.
 *
 *  Use of this source code is governed by a BSD-style license
 *  that can be found in the LICENSE file in the root of the source
 *  tree.
 */

'use strict';

function startCapture(){
// Put variables in global scope to make them available to the browser console.
  const video = document.querySelector('video#capture-video');
  const canvas = window.canvas = document.getElementById('capture-canvas');
  const button = document.getElementById('capture-button');
  const save_button = document.getElementById('save-button');
  const try_again = document.getElementById('retry-button');

  video.hidden = false;
  canvas.hidden = true;
  button.hidden = false;
  save_button.hidden = true;
  try_again.hidden = true;

  canvas.width = 0;
  canvas.height = 0;

  button.onclick = function() {
    canvas.hidden = false;
    save_button.hidden = false;
    try_again.hidden = false;
    button.hidden = true;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    save_button.hidden = false;
    video.hidden = true;
  };
  try_again.onclick = function () {
    canvas.hidden = true;
    video.hidden = false;
    save_button.hidden = true;
    try_again.hidden = true;
    button.hidden = false;
  };
  save_button.onclick = function () {
    const img = canvas.toDataURL();
    const event = new CustomEvent('save-capture', {detail: img});
    document.dispatchEvent(event);
  };
  const constraints = {
    audio: false,
    video: true
  };

  function handleSuccess(stream) {
    window.stream = stream; // make stream available to browser console
    video.srcObject = stream;
  }

  function handleError(error) {
    console.log('navigator.MediaDevices.getUserMedia error: ', error.message, error.name);
  }

  navigator.mediaDevices.getUserMedia(constraints).then(handleSuccess).catch(handleError);
}
