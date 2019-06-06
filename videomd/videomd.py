"""Functions for reading and generating VideoMD Data Dictionaries as
xml.etree.ElementTree data structures.

References:

    * VideoMD: https://www.loc.gov/standards/vmdvmd/
    * Schema documentation:
      https://www.loc.gov/standards/amdvmd/htmldoc/videoMD.html

"""
import lxml.etree as ET
from xml_helpers.utils import xsi_ns, XSI_NS


VIDEOMD_NS = 'http://www.loc.gov/videoMD/'
NAMESPACE = {"vmd": VIDEOMD_NS, "xsi": XSI_NS}

MEDIA_PARAMS = [
    "tracking", "duration", "language",
    "security", "size", "dataRate",
    "timecode", "use", "otherUse"
]

FILE_DATA_PARAMS = MEDIA_PARAMS + [
    "bitsPerSample", "byteOrder", "color",
    "otherColor", "messageDigest", "compression",
    "track", "dataRateUnit", "dataRateMode",
    "frame", "frameRate", "sampleRate",
    "location", "format", "sampling",
    "signalFormat", "sound"
]


PHYSICAL_DATA_PARAMS = [
    "EBUStorageMediaCodes", "colorBurst", "condition",
    "dimensions", "disposition", "dtv",
    "generation", "material", "numberCarriers",
    "physFormat", "signalFormat", "timecode",
    "tracking", "videodiscType", "videotapeType",
    "note"
]

TRACK_PARAMS = MEDIA_PARAMS + [
    "bitsPerSample", "bitsPerPixelStored", "codec",
    "compressionRatio", "quality", "frame",
    "frameRate", "sampleRate", "sampling",
    "sampleCount", "signalFormat"
]

FORMAT_PARAMS = [
    "annotation", "creatorApp", "creatorLib",
    "creatorLibDate", "creatorLibSettings", "name",
    "encodingDate", "TaggedDate", "commercialName",
    "mimetype", "profile", "settings",
    "version"
]

CODEC_PARAMS = FORMAT_PARAMS + [
    "codecID", "channelCount", "endianness",
    "scanType", "scanOrder", "sign"
]

DIMENSIONS_PARAMS = [
    "DEPTH", "DIAMETER", "GAUGE",
    "HEIGHT", "LENGTH", "NOTE",
    "THICKNESS", "UNITS", "WIDTH"
]

MATERIAL_PARAMS = [
    "baseMaterial", "binder", "discSurface",
    "oxide", "activeLayer", "reflectiveLayer",
    "stockBrand", "method", "usedSides"
]

VARIABLE_RATE_PARAMS = [
    "maximum", "minimum", "mode",
    "nominal", "unit"
]


def videomd_ns(tag, prefix=""):
    """Prefix ElementTree tags with VideoMD namespace.

    object -> {http://www.loc.gov/VideoMD}object

    :tag: Tag name as string
    :returns: Prefixed tag

    """
    if prefix:
        tag = tag[0].upper() + tag[1:]
        return '{%s}%s%s' % (VIDEOMD_NS, prefix, tag)
    return '{%s}%s' % (VIDEOMD_NS, tag)


def _element(tag, prefix=""):
    """Return _ElementInterface with VideoMD namespace.

    Prefix parameter is useful for adding prefixed to lower case tags. It just
    uppercases first letter of tag and appends it to prefix::

        element = _element('objectIdentifier', 'linking')
        element.tag
        'linkingObjectIdentifier'

    :tag: Tagname
    :prefix: Prefix for the tag (default="")
    :returns: ElementTree element object

    """
    return ET.Element(videomd_ns(tag, prefix), nsmap=NAMESPACE)


def _subelement(parent, tag, prefix=""):
    """Return subelement for the given parent element. Created element is
    appelded to parent element.

    :parent: Parent element
    :tag: Element tagname
    :prefix: Prefix for the tag
    :returns: Created subelement
    """
    return ET.SubElement(parent, videomd_ns(tag, prefix))


def _simple_elements(parent, element_values, element_name):
    """Add new simple elements to a parent element. If a list of values are
    given, then as many elements are created than there are values in the
    list.
    :parent: Parent element
    :element_values: String or list of strings of the simple element values
    :element_name: Element name.
    """
    if element_values is not None:

        if isinstance(element_values, list):
            for value in element_values:
                vmd_element = _subelement(parent, element_name)
                vmd_element.text = value
        else:
            vmd_element = _subelement(parent, element_name)
            vmd_element.text = element_values


def _add_elements(parent, elements):
    """Add given element to a parent element.
    :parent element: Parent element
    :elements: Element to be added
    """
    if elements is not None:

        if isinstance(elements, list):
            for element in elements:
                parent.append(element)
        else:
            parent.append(elements)


def _location(location, loc_type):
    """Creates VideoMD location element
    :location: Location value
    :loc_type: Type of the location element
    :returns: VideoMD location element
    """
    loc_elem = _element('location')
    loc_elem.text = location

    if loc_type is None:
        return loc_elem

    if loc_type in ['URN', 'URL', 'PURL', 'HANDLE', 'DOI']:
        loc_elem.set('type', loc_type)
    else:
        loc_elem.set('type', 'OTHER')
        loc_elem.set('otherType', loc_type)

    return loc_elem


def _variable_rate(key, rate, attr_dict):
    """Creates VideoMD frameRate or sampleRate with attributes
    :key: Element name of the variable rate element
    :rate: Rate given as value to the element
    :attr_dict: Attribute values as dict to the variable rate element
    :returns: videoMd variable rate element
    """
    elem = _element(key)
    elem.text = rate

    if attr_dict is None:
        return elem

    for subkey in VARIABLE_RATE_PARAMS:
        if subkey in attr_dict:
            elem.set(subkey, attr_dict[subkey])

    return elem


def get_params(param_list):
    """Initialize all parameters as None
    :param_list: List of parameter names
    :returns: Dict of parameters
    """

    params = {}
    for key in param_list:
        params[key] = None

    return params


def _check_params(param_dict, param_list):
    """Check that all the provided parameters in param_dict
    are found in the param_list.
    :param_dict: Dict of parameters
    :param_list: List of parameter names
    """

    for key in param_dict:
        if key not in param_list:
            raise ValueError("Parameter: '%s' not recognized" % key)


def create_videomd(analog_digital_flag='FileDigital', file_data=None,
                   physical_data=None, video_info=None, calibration_info=None):
    """Create VideoMD Data Dictionary root element.
    :analog_digital_flag: ANALOGDIGITALFLAG attribute value
    :file_data: VideoMD fileData element
    :physical_data: VideoMD physicalData element
    :video_info: VideoMD videoInfo element
    :calibration_info: VideoMD calibrationInfo element
    :returns: VideoMD metadata
    """
    videomd_elem = _element('VIDEOMD')
    videomd_elem.set(
        xsi_ns('schemaLocation'),
        'http://www.loc.gov/VideoMD/ ' +
        'https://www.loc.gov/standards/vmdvmd/VideoMD.xsd'
    )
    videomd_elem.set('ANALOGDIGITALFLAG', analog_digital_flag)

    if file_data is not None:
        videomd_elem.append(file_data)
    if physical_data is not None:
        videomd_elem.append(physical_data)
    if video_info is not None:
        videomd_elem.append(video_info)
    if calibration_info is not None:
        videomd_elem.append(calibration_info)

    return videomd_elem


def vmd_file_data(params, drate_attr=None, frate_attr=None,
                  srate_attr=None, location_type=None):
    """Creates VideoMD fileData element
    :params: Dict of parameters listed in FILE_DATA_PARAMS
    :drate_attr: Dict of attributes for dataRate element
    :frate_attr: Dict of attributes for frameRate element
    :srate_attr: Dict of attributes for sampleRate element
    :location_type: Type of the location element
    :returns: VideoMD fileData element
    """
    _check_params(params, FILE_DATA_PARAMS)

    attr_dict = {
        "dataRate": drate_attr,
        "frameRate": frate_attr,
        "sampleRate": srate_attr
    }

    element = _element('fileData')

    for key in FILE_DATA_PARAMS:
        if key in params and params[key] is not None:
            if key in ["tracking", "timecode", "messageDigest",
                       "compression", "track", "frame", "format"]:
                _add_elements(element, params[key])
            elif key == "location":
                _add_elements(element, _location(params[key], location_type))
            elif key in ["dataRate", "frameRate", "sampleRate"]:
                _add_elements(
                    element, _variable_rate(key, params[key], attr_dict[key]))
            else:
                _simple_elements(element, params[key], key)

    return element


def vmd_format(params):
    """Creates VideoMD format element
    :params: Dict of parameters listed in FORMAT_PARAMS
    :returns: VideoMD format element
    """
    _check_params(params, FORMAT_PARAMS)

    element = _element('format')

    for key in FORMAT_PARAMS:
        if key in params and params[key] is not None:
            _simple_elements(element, params[key], key)

    return element


def vmd_codec(params):
    """Creates VideoMD codec element
    :params: Dict of parameters listed in CODEC_PARAMS
    :returns: VideoMD codec element
    """
    _check_params(params, CODEC_PARAMS)

    element = _element('codec')

    for key in CODEC_PARAMS:
        if key in params and params[key] is not None:
            _simple_elements(element, params[key], key)

    return element


def vmd_timecode(record_method=None, timecode_type=None,
                 initial_value=None):
    """Creates VideoMD timecode element
    :record_method: Value of timecodeRecordMethod element
    :timecode_type: Value of timecodeType element
    :initial_value: Value of timecodeInitialValue element
    :returns: VideoMD timecode element
    """
    timecode_elem = _element('timecode')

    _simple_elements(timecode_elem, record_method, 'timecodeRecordMethod')
    _simple_elements(timecode_elem, timecode_type, 'timecodeType')
    _simple_elements(timecode_elem, initial_value, 'timecodeInitialValue')

    return timecode_elem


def vmd_message_digest(datetime, algorithm, message_digest):
    """Creates VideoMD messageDigest element
    :datetime: Value of messageDigestDatetime element
    :algorithm: Value of messageDigestAlgorithm element
    :message_digest: Value of messageDigest element
    :returns: VideoMD messageDigest element
    """
    message_digest_elem = _element('messageDigest')

    _simple_elements(message_digest_elem, datetime, 'messageDigestDatetime')
    _simple_elements(message_digest_elem, algorithm, 'messageDigestAlgorithm')
    _simple_elements(message_digest_elem, message_digest, 'messageDigest')

    return message_digest_elem


def vmd_compression(app=None, app_version=None, name=None, quality=None):
    """Creates VideoMD compression element
    :app: Value of codecCreatorApp element
    :app_version: Value of codecCreatorAppVersion element
    :name: Value of codecName element
    :quality: Value of codecQuality element
    :returns: VideoMD compression element
    """
    compression_elem = _element('compression')

    _simple_elements(compression_elem, app, 'codecCreatorApp')
    _simple_elements(compression_elem, app_version, 'codecCreatorAppVersion')
    _simple_elements(compression_elem, name, 'codecName')
    _simple_elements(compression_elem, quality, 'codecQuality')

    return compression_elem


def vmd_track(params, track_num=None, track_type=None,
              drate_attr=None, frate_attr=None, srate_attr=None):
    """Creates VideoMD track element
    :params: Dict of parameters listed in TRACK_PARAMS
    :track_num: Value of the num attribute in track element
    :track_type: Value of the type attribute in track element
    :drate_attr: Dict of attributes for dataRate element
    :frate_attr: Dict of attributes for frameRate element
    :srate_attr: Dict of attributes for sampleRate element
    :returns: VideoMD track element
    """
    _check_params(params, TRACK_PARAMS)

    attr_dict = {
        "dataRate": drate_attr,
        "frameRate": frate_attr,
        "sampleRate": srate_attr
    }

    track_elem = _element('track')

    if track_num is not None:
        track_elem.set('num', track_num)
    if track_type is not None:
        track_elem.set('type', track_type)

    for key in TRACK_PARAMS:
        if key in params and params[key] is not None:
            if key in ["tracking", "timecode", "codec", "frame"]:
                _add_elements(track_elem, params[key])
            elif key in ["dataRate", "frameRate", "sampleRate"]:
                _add_elements(
                    track_elem,
                    _variable_rate(key, params[key], attr_dict[key]))
            else:
                _simple_elements(track_elem, params[key], key)

    return track_elem


def vmd_physical_data(params):
    """Creates VideoMD physicalData element
    :params: Dict of parameters listed in PHYSICAL_DATA_PARAMS
    :returns: VideoMD physicalData element
    """
    _check_params(params, PHYSICAL_DATA_PARAMS)

    physical_data_elem = _element('physicalData')

    for key in PHYSICAL_DATA_PARAMS:
        if key in params and params[key] is not None:
            if key in ["dimensions", "dtv", "material", "timecode",
                       "tracking"]:
                _add_elements(physical_data_elem, params[key])
            else:
                _simple_elements(physical_data_elem, params[key], key)

    return physical_data_elem


def vmd_dtv(aspect_ratio=None, note=None, resolution=None, scan=None):
    """Creates VideoMD dtv element
    :aspect_ratio: Value of dtvAspectRatio element
    :note: Value of dtvNote element
    :resolution: Value of dtvResolution element
    :scan: Value of dtvScan element
    :returns: VideoMD dtv element
    """
    dtv_elem = _element('dtv')

    _simple_elements(dtv_elem, aspect_ratio, 'dtvAspectRatio')
    _simple_elements(dtv_elem, note, 'dtvNote')
    _simple_elements(dtv_elem, resolution, 'dtvResolution')
    _simple_elements(dtv_elem, scan, 'dtvScan')

    return dtv_elem


def vmd_dimensions(params):
    """Creates VideoMD dimensions element
    :params: Dict of parameters listed in DIMENSIONS_PARAMS
    :returns: VideoMD dimensions element
    """
    _check_params(params, DIMENSIONS_PARAMS)

    dimensions_elem = _element('dimensions')

    for key in DIMENSIONS_PARAMS:
        if key in params and params[key] is not None:
            dimensions_elem.set(key, params[key])

    return dimensions_elem


def vmd_material(params):
    """Creates VideoMD material element
    :params: Dict of parameters listed in MATERIAL_PARAMS
    :returns: VideoMD material element
    """
    _check_params(params, MATERIAL_PARAMS)

    material_elem = _element('material')

    for key in MATERIAL_PARAMS:
        if key in params and params[key] is not None:
            _simple_elements(material_elem, params[key], key)

    return material_elem


def vmd_tracking(tracking_type=None, tracking_value=None):
    """Creates VideoMD tracking element
    :tracking_type: Value of trackingType element
    :tracking_value: Value of trackingValue element
    :returns: VideoMD tracking element
    """
    tracking_elem = _element('tracking')

    _simple_elements(tracking_elem, tracking_type, 'trackingType')
    _simple_elements(tracking_elem, tracking_value, 'trackingValue')

    return tracking_elem


def vmd_frame(pixels_horizontal=None, pixels_vertical=None,
              frame_rate=None, par=None, dar=None, rotation=None):
    """Creates VideoMD frame element
    :pixels_horizontal: Value of pixelsHorizontal element
    :pixels_vertical: Value of pixelsVertical element
    :frame_rate: Value of frameRate element
    :par: Value of PAR element
    :dar: Value of DAR element
    :rotation: Value of rotation element
    :returns: VideoMD frame element
    """
    frame_elem = _element('frame')

    _simple_elements(frame_elem, pixels_horizontal, 'pixelsHorizontal')
    _simple_elements(frame_elem, pixels_vertical, 'pixelsVertical')
    _simple_elements(frame_elem, frame_rate, 'frameRate')
    _simple_elements(frame_elem, par, 'PAR')
    _simple_elements(frame_elem, dar, 'DAR')
    _simple_elements(frame_elem, rotation, 'rotation')

    return frame_elem


def vmd_video_info(
        aspect_ratio=None, closed_captioning_note=None,
        closed_captioning_type=None, dimensions=None,
        duration=None, frame=None, note=None):
    """Creates VideoMD videoInfo element
    :aspect_ratio: Value of aspectRatio element
    :closed_captioning_note: Value of closedCaptioningNote element
    :closed_captioning_type: Value of closedCaptioningType element
    :dimensions: Dimensions element
    :duration: Value of duration element
    :frame: Frame element
    :note: Value of note element
    :returns: VideoMD videoInfo element
    """
    video_info_elem = _element('videoInfo')

    _simple_elements(video_info_elem, aspect_ratio, 'aspectRatio')
    _simple_elements(video_info_elem, closed_captioning_note,
                     'closedCaptioningNote')
    _simple_elements(video_info_elem, closed_captioning_type,
                     'closedCaptioningType')
    _add_elements(video_info_elem, dimensions)
    _simple_elements(video_info_elem, duration, 'duration')
    _add_elements(video_info_elem, frame)
    _simple_elements(video_info_elem, note, 'note')

    return video_info_elem


def vmd_calibration_info(
        image_data=None, target_id=None, target_type=None):
    """Creates VideoMD calibrationInfo element
    :image_data: Value of imageData element
    :target_id: Value of targetId element
    :target_type: Value of targetType element
    :returns: VideoMD calibrationInfo element
    """
    calibration_info_elem = _element('calibrationInfo')

    _simple_elements(calibration_info_elem, image_data, 'imageData')
    _simple_elements(calibration_info_elem, target_id, 'targetId')
    _simple_elements(calibration_info_elem, target_type, 'targetType')

    return calibration_info_elem
