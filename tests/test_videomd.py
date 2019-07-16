"""Unit tests for creation of VideoMD metadata.
"""
from __future__ import unicode_literals

import pytest
import lxml.etree as ET
from copy import deepcopy
import videomd as vmd


NAMESPACES = {'vmd': vmd.VIDEOMD_NS}
SCHEMA = ET.XMLSchema(ET.parse("tests/schemas/videoMD.xsd"))


def _get_elems(root, path):
    return root.xpath(path, namespaces=NAMESPACES)


def test_videomd():
    """Test that create_videomd() functions returns the
    root XML elements with correct metadata.
    """

    compression = vmd.vmd_compression(
        app='(:unap)',
        app_version='(:unap)',
        name='(:unap)',
        quality='lossless'
    )
    frame = vmd.vmd_frame(
        pixels_horizontal='1920',
        pixels_vertical='1080',
        par='1.0',
        dar='16/9'
    )

    params = vmd.get_params(vmd.FILE_DATA_PARAMS)
    params["duration"] = "PT1H30M"
    params["bitsPerSample"] = "24"
    params["color"] = "Color"
    params["compression"] = compression
    params["dataRate"] = "8"
    params["dataRateMode"] = "Fixed"
    params["frame"] = frame
    params["frameRate"] = "24"
    params["sampling"] = "4:4:4"
    params["signalFormat"] = "PAL"

    file_data = vmd.vmd_file_data(params)
    video_info = vmd.vmd_video_info(duration="PT1H30M", frame=deepcopy(frame))
    videomd = vmd.create_videomd(file_data=file_data, video_info=video_info)

    SCHEMA.assertValid(videomd)

    path = "/vmd:VIDEOMD[@ANALOGDIGITALFLAG='FileDigital']"
    assert len(videomd.xpath(path, namespaces=NAMESPACES)) == 1

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:duration"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == 'PT1H30M'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:bitsPerSample"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '24'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:color"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == 'Color'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:compression/vmd:codecCreatorApp"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '(:unap)'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:compression/" \
           "vmd:codecCreatorAppVersion"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '(:unap)'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:compression/vmd:codecName"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '(:unap)'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:compression/vmd:codecQuality"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == 'lossless'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:dataRate"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '8'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:dataRateMode"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == 'Fixed'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:frame/vmd:pixelsHorizontal"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '1920'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:frame/vmd:pixelsVertical"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '1080'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:frame/vmd:PAR"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '1.0'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:frame/vmd:DAR"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '16/9'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:frameRate"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '24'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:sampling"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '4:4:4'

    path = "/vmd:VIDEOMD/vmd:fileData/vmd:signalFormat"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == 'PAL'

    path = "/vmd:VIDEOMD/vmd:videoInfo/vmd:duration"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == 'PT1H30M'

    path = "/vmd:VIDEOMD/vmd:videoInfo/vmd:frame/vmd:pixelsHorizontal"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '1920'

    path = "/vmd:VIDEOMD/vmd:videoInfo/vmd:frame/vmd:pixelsVertical"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '1080'

    path = "/vmd:VIDEOMD/vmd:videoInfo/vmd:frame/vmd:PAR"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '1.0'

    path = "/vmd:VIDEOMD/vmd:videoInfo/vmd:frame/vmd:DAR"
    assert videomd.xpath(path, namespaces=NAMESPACES)[0].text == '16/9'


def test_videomd_param_fail():
    """Test that ValueError is raised if any of the provided
    parameters is not recognized.
    """

    params = {"typo": None}

    with pytest.raises(ValueError):
        vmd.vmd_file_data(params)

    with pytest.raises(ValueError):
        vmd.vmd_format(params)

    with pytest.raises(ValueError):
        vmd.vmd_track(params)

    with pytest.raises(ValueError):
        vmd.vmd_physical_data(params)

    with pytest.raises(ValueError):
        vmd.vmd_dimensions(params)

    with pytest.raises(ValueError):
        vmd.vmd_material(params)


@pytest.mark.parametrize("rate", [
    'dataRate', 'frameRate', 'sampleRate'])
def test_variable_rate_file_data(rate):
    """Test variable rate attribute arguments in vmd_file_data()
    """
    attr = {"maximum": "10", "minimum": "6", "unit": "Mbps"}

    if rate == "dataRate":
        root = vmd.vmd_file_data({rate: "8"}, drate_attr=attr)
    elif rate == "frameRate":
        root = vmd.vmd_file_data({rate: "8"}, frate_attr=attr)
    else:
        root = vmd.vmd_file_data({rate: "8"}, srate_attr=attr)

    path = "/vmd:fileData/vmd:" + rate + "/@maximum"
    assert root.xpath(path, namespaces=NAMESPACES)[0] == '10'

    path = "/vmd:fileData/vmd:" + rate + "/@minimum"
    assert root.xpath(path, namespaces=NAMESPACES)[0] == '6'

    path = "/vmd:fileData/vmd:" + rate + "/@unit"
    assert root.xpath(path, namespaces=NAMESPACES)[0] == 'Mbps'


@pytest.mark.parametrize("rate", [
    'dataRate', 'frameRate', 'sampleRate'])
def test_variable_rate_track(rate):
    """Test variable rate attribute arguments in vmd_track()
    """
    attr = {"maximum": "10", "minimum": "6", "unit": "Mbps"}

    if rate == "dataRate":
        root = vmd.vmd_track({rate: "8"}, drate_attr=attr)
    elif rate == "frameRate":
        root = vmd.vmd_track({rate: "8"}, frate_attr=attr)
    else:
        root = vmd.vmd_track({rate: "8"}, srate_attr=attr)

    path = "/vmd:track/vmd:" + rate + "/@maximum"
    assert root.xpath(path, namespaces=NAMESPACES)[0] == '10'

    path = "/vmd:track/vmd:" + rate + "/@minimum"
    assert root.xpath(path, namespaces=NAMESPACES)[0] == '6'

    path = "/vmd:track/vmd:" + rate + "/@unit"
    assert root.xpath(path, namespaces=NAMESPACES)[0] == 'Mbps'


def test_location_attribute():
    """Test attributes in videoMD location element
    """
    root = vmd.vmd_file_data({"location": "foo"}, location_type="bar")
    path = "/vmd:fileData/vmd:location"
    assert root.xpath(path, namespaces=NAMESPACES)[0].text == 'foo'
    path = "/vmd:fileData/vmd:location/@type"
    assert root.xpath(path, namespaces=NAMESPACES)[0] == 'OTHER'
    path = "/vmd:fileData/vmd:location/@otherType"
    assert root.xpath(path, namespaces=NAMESPACES)[0] == 'bar'


def test_timecode():
    """Test that vmd_timecode() produces correct XML element
    """
    root = vmd.vmd_timecode("foo", "bar", "zzz")

    tc_method = _get_elems(
        root, "/vmd:timecode/vmd:timecodeRecordMethod")[0].text
    tc_type = _get_elems(
        root, "/vmd:timecode/vmd:timecodeType")[0].text
    tc_value = _get_elems(
        root, "/vmd:timecode/vmd:timecodeInitialValue")[0].text

    assert tc_method == "foo"
    assert tc_type == "bar"
    assert tc_value == "zzz"


def test_track():
    """Test that vmd_track() produces correct XML element
    """
    frame = vmd.vmd_frame(
        pixels_horizontal='1920',
        pixels_vertical='1080',
        par='1.0',
        dar='16/9'
    )

    params = vmd.get_params(vmd.TRACK_PARAMS)
    params["duration"] = "PT1H30M"
    params["bitsPerSample"] = "24"
    params["compressionRatio"] = "0.5"
    params["quality"] = "lossy"
    params["frame"] = frame
    params["frameRate"] = "24"
    params["sampleRate"] = "3000"
    params["sampling"] = "4:4:4"
    params["signalFormat"] = "PAL"

    track = vmd.vmd_track(params)

    path = "/vmd:track/vmd:duration"
    assert track.xpath(path, namespaces=NAMESPACES)[0].text == 'PT1H30M'

    path = "/vmd:track/vmd:bitsPerSample"
    assert track.xpath(path, namespaces=NAMESPACES)[0].text == '24'

    path = "/vmd:track/vmd:compressionRatio"
    assert track.xpath(path, namespaces=NAMESPACES)[0].text == '0.5'

    path = "/vmd:track/vmd:quality"
    assert track.xpath(path, namespaces=NAMESPACES)[0].text == 'lossy'

    path = "/vmd:track/vmd:frameRate"
    assert track.xpath(path, namespaces=NAMESPACES)[0].text == '24'

    path = "/vmd:track/vmd:sampleRate"
    assert track.xpath(path, namespaces=NAMESPACES)[0].text == '3000'

    path = "/vmd:track/vmd:sampling"
    assert track.xpath(path, namespaces=NAMESPACES)[0].text == '4:4:4'

    path = "/vmd:track/vmd:signalFormat"
    assert track.xpath(path, namespaces=NAMESPACES)[0].text == 'PAL'

    path = "/vmd:track/vmd:frame/vmd:pixelsHorizontal"
    assert track.xpath(path, namespaces=NAMESPACES)[0].text == '1920'

    path = "/vmd:track/vmd:frame/vmd:pixelsVertical"
    assert track.xpath(path, namespaces=NAMESPACES)[0].text == '1080'

    path = "/vmd:track/vmd:frame/vmd:PAR"
    assert track.xpath(path, namespaces=NAMESPACES)[0].text == '1.0'

    path = "/vmd:track/vmd:frame/vmd:DAR"
    assert track.xpath(path, namespaces=NAMESPACES)[0].text == '16/9'


def test_track_attribute():
    """Test attributes in videoMD track element
    """
    root = vmd.vmd_track({}, track_num="foo", track_type="bar")
    path = "/vmd:track/@num"
    assert root.xpath(path, namespaces=NAMESPACES)[0] == 'foo'
    path = "/vmd:track/@type"
    assert root.xpath(path, namespaces=NAMESPACES)[0] == 'bar'


def test_codec():
    """Test that vmd_codec() produces correct XML element
    """
    params = vmd.get_params(vmd.CODEC_PARAMS)
    params["name"] = "foo"
    params["channelCount"] = "1"
    params["scanType"] = "bar"

    codec = vmd.vmd_codec(params)

    path = "/vmd:codec/vmd:name"
    assert codec.xpath(path, namespaces=NAMESPACES)[0].text == 'foo'

    path = "/vmd:codec/vmd:channelCount"
    assert codec.xpath(path, namespaces=NAMESPACES)[0].text == '1'

    path = "/vmd:codec/vmd:scanType"
    assert codec.xpath(path, namespaces=NAMESPACES)[0].text == 'bar'


def test_format():
    """Test that vmd_format() produces correct XML element
    """
    params = vmd.get_params(vmd.FORMAT_PARAMS)
    params["name"] = "TIFF"
    params["mimetype"] = "image/tiff"
    params["version"] = "6.0"

    format_elem = vmd.vmd_format(params)

    path = "/vmd:format/vmd:name"
    assert format_elem.xpath(path, namespaces=NAMESPACES)[0].text == 'TIFF'

    path = "/vmd:format/vmd:mimetype"
    assert format_elem.xpath(
        path, namespaces=NAMESPACES)[0].text == 'image/tiff'

    path = "/vmd:format/vmd:version"
    assert format_elem.xpath(path, namespaces=NAMESPACES)[0].text == '6.0'


def test_dtv():
    """Test that vmd_dtv() produces correct XML element
    """
    dtv = vmd.vmd_dtv("foo1", "foo2", "foo3", "foo4")

    path = "/vmd:dtv/vmd:dtvAspectRatio"
    assert dtv.xpath(path, namespaces=NAMESPACES)[0].text == "foo1"

    path = "/vmd:dtv/vmd:dtvNote"
    assert dtv.xpath(path, namespaces=NAMESPACES)[0].text == "foo2"

    path = "/vmd:dtv/vmd:dtvResolution"
    assert dtv.xpath(path, namespaces=NAMESPACES)[0].text == "foo3"

    path = "/vmd:dtv/vmd:dtvScan"
    assert dtv.xpath(path, namespaces=NAMESPACES)[0].text == "foo4"


def test_message_digest():
    """Test that vmd_message_digest() produces correct XML element
    """
    root = vmd.vmd_message_digest("datetime", "algorithm", "message")

    path = "/vmd:messageDigest/vmd:messageDigest"

    message = _get_elems(root, path)[0].text
    datetime = _get_elems(root, path + "Datetime")[0].text
    algorithm = _get_elems(root, path + "Algorithm")[0].text

    assert message == "message"
    assert datetime == "datetime"
    assert algorithm == "algorithm"


def test_compression():
    """Test that vmd_compression() produces correct XML element
    """
    root = vmd.vmd_compression("app", "app_version", "name", "quality")

    path = "/vmd:compression/vmd:codec"

    app = _get_elems(root, path + "CreatorApp")[0].text
    app_version = _get_elems(root, path + "CreatorAppVersion")[0].text
    name = _get_elems(root, path + "Name")[0].text
    quality = _get_elems(root, path + "Quality")[0].text

    assert app == "app"
    assert app_version == "app_version"
    assert name == "name"
    assert quality == "quality"


def test_physical_data():
    """Test that vmd_physical_data() produces correct XML element
    """
    params = vmd.get_params(vmd.PHYSICAL_DATA_PARAMS)
    params["condition"] = "condition"
    params["disposition"] = "disposition"

    root = vmd.vmd_physical_data(params)

    path = "/vmd:physicalData/vmd:"

    condition = _get_elems(root, path + "condition")[0].text
    disposition = _get_elems(root, path + "disposition")[0].text

    assert condition == "condition"
    assert disposition == "disposition"


def test_dimensions():
    """Test that vmd_dimensions() produces correct XML element
    """
    params = {"DEPTH": "DEPTH", "DIAMETER": "DIAMETER"}

    root = vmd.vmd_dimensions(params)

    assert root.get("DEPTH") == "DEPTH"
    assert root.get("DIAMETER") == "DIAMETER"


def test_material():
    """Test that vmd_material() produces correct XML element
    """
    params = vmd.get_params(vmd.MATERIAL_PARAMS)
    params["baseMaterial"] = "baseMaterial"
    params["binder"] = "binder"

    root = vmd.vmd_material(params)

    path = "/vmd:material/vmd:"

    base_material = _get_elems(root, path + "baseMaterial")[0].text
    binder = _get_elems(root, path + "binder")[0].text

    assert base_material == "baseMaterial"
    assert binder == "binder"


def test_tracking():
    """Test that vmd_tracking() produces correct XML element
    """
    root = vmd.vmd_tracking("trackingType", "trackingValue")
    path = "/vmd:tracking/vmd:tracking"

    tracking_type = _get_elems(root, path + "Type")[0].text
    tracking_value = _get_elems(root, path + "Value")[0].text

    assert tracking_type == "trackingType"
    assert tracking_value == "trackingValue"


def test_calibration_info():
    """Test that vmd_calibration_info() produces correct XML element
    """
    root = vmd.vmd_calibration_info(image_data="foo",
                                    target_id="bar")
    path = "/vmd:calibrationInfo/vmd:"

    image_data = _get_elems(root, path + "imageData")[0].text
    target_id = _get_elems(root, path + "targetId")[0].text

    assert image_data == "foo"
    assert target_id == "bar"
