<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis maxScale="0" simplifyAlgorithm="0" readOnly="0" version="3.3.0-Master" hasScaleBasedVisibilityFlag="0" minScale="1e+08" simplifyDrawingTol="1" simplifyDrawingHints="0" simplifyLocal="1" labelsEnabled="0" simplifyMaxScale="1">
  <renderer-v2 type="singleSymbol" symbollevels="0" enableorderby="0" forceraster="0">
    <symbols>
      <symbol type="marker" name="0" alpha="1" clip_to_extent="1">
        <layer locked="0" pass="0" class="SvgMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="255,0,0,255"/>
          <prop k="fixedAspectRatio" v="0"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="name" v="arrows/Arrow_06.svg"/>
          <prop k="offset" v="0.00000000000000006,-3.00000000000000044"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="6"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option type="Map" name="properties">
                <Option type="Map" name="angle">
                  <Option type="bool" name="active" value="true"/>
                  <Option type="QString" name="field" value="azimuth"/>
                  <Option type="int" name="type" value="2"/>
                </Option>
              </Option>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
        <layer locked="0" pass="0" class="SvgMarker" enabled="1">
          <prop k="angle" v="0"/>
          <prop k="color" v="0,0,0,255"/>
          <prop k="fixedAspectRatio" v="0"/>
          <prop k="horizontal_anchor_point" v="1"/>
          <prop k="name" v="gpsicons/camera.svg"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="255,255,255,255"/>
          <prop k="outline_width" v="0"/>
          <prop k="outline_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="scale_method" v="diameter"/>
          <prop k="size" v="4"/>
          <prop k="size_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="size_unit" v="MM"/>
          <prop k="vertical_anchor_point" v="1"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer diagramType="Histogram" attributeLegend="1">
    <DiagramCategory penColor="#000000" opacity="1" sizeType="MM" minScaleDenominator="0" barWidth="5" rotationOffset="270" maxScaleDenominator="1e+08" scaleBasedVisibility="0" scaleDependency="Area" backgroundColor="#ffffff" height="15" penAlpha="255" backgroundAlpha="255" sizeScale="3x:0,0,0,0,0,0" penWidth="0" diagramOrientation="Up" lineSizeScale="3x:0,0,0,0,0,0" labelPlacementMethod="XHeight" enabled="0" minimumSize="0" lineSizeType="MM" width="15">
      <fontProperties description="Sans Serif,9,-1,5,50,0,0,0,0,0" style=""/>
      <attribute color="#000000" label="" field=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings dist="0" placement="0" priority="0" obstacle="0" zIndex="0" showAll="1" linePlacementFlags="2">
    <properties>
      <Option type="Map">
        <Option type="QString" name="name" value=""/>
        <Option name="properties"/>
        <Option type="QString" name="type" value="collection"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <fieldConfiguration>
    <field name="filepath">
      <editWidget type="ExternalResource">
        <config>
          <Option type="Map">
            <Option type="int" name="DocumentViewer" value="1"/>
            <Option type="int" name="DocumentViewerHeight" value="0"/>
            <Option type="int" name="DocumentViewerWidth" value="0"/>
            <Option type="bool" name="FileWidget" value="true"/>
            <Option type="bool" name="FileWidgetButton" value="true"/>
            <Option type="QString" name="FileWidgetFilter" value=""/>
            <Option type="Map" name="PropertyCollection">
              <Option type="QString" name="name" value=""/>
              <Option type="Unknown" name="properties" value=""/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
            <Option type="int" name="RelativeStorage" value="0"/>
            <Option type="int" name="StorageMode" value="0"/>
          </Option>
        </config>
      </editWidget>
    </field>
    <field name="longitude">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="latitude">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="altitude">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="north">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="azimuth">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="gps_date">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="img_date">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias name="" index="0" field="filepath"/>
    <alias name="" index="1" field="longitude"/>
    <alias name="" index="2" field="latitude"/>
    <alias name="" index="3" field="altitude"/>
    <alias name="" index="4" field="north"/>
    <alias name="" index="5" field="azimuth"/>
    <alias name="" index="6" field="gps_date"/>
    <alias name="" index="7" field="img_date"/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default applyOnUpdate="0" expression="" field="filepath"/>
    <default applyOnUpdate="0" expression="" field="longitude"/>
    <default applyOnUpdate="0" expression="" field="latitude"/>
    <default applyOnUpdate="0" expression="" field="altitude"/>
    <default applyOnUpdate="0" expression="" field="north"/>
    <default applyOnUpdate="0" expression="" field="azimuth"/>
    <default applyOnUpdate="0" expression="" field="gps_date"/>
    <default applyOnUpdate="0" expression="" field="img_date"/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="filepath"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="longitude"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="latitude"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="altitude"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="north"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="azimuth"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="gps_date"/>
    <constraint exp_strength="0" notnull_strength="0" constraints="0" unique_strength="0" field="img_date"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" desc="" field="filepath"/>
    <constraint exp="" desc="" field="longitude"/>
    <constraint exp="" desc="" field="latitude"/>
    <constraint exp="" desc="" field="altitude"/>
    <constraint exp="" desc="" field="north"/>
    <constraint exp="" desc="" field="azimuth"/>
    <constraint exp="" desc="" field="gps_date"/>
    <constraint exp="" desc="" field="img_date"/>
  </constraintExpressions>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
    <actionsetting notificationMessage="" type="5" name="Open file" id="{bb28fa30-3c43-4408-a6dc-ce5ff67559f9}" action="[%filepath%]" isEnabledOnlyWhenEditable="0" shortTitle="" capture="0" icon="">
      <actionScope id="Feature"/>
      <actionScope id="Canvas"/>
      <actionScope id="Field"/>
    </actionsetting>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortOrder="0" sortExpression="">
    <columns>
      <column hidden="0" type="field" width="-1" name="filepath"/>
      <column hidden="0" type="field" width="-1" name="longitude"/>
      <column hidden="0" type="field" width="-1" name="latitude"/>
      <column hidden="0" type="field" width="-1" name="altitude"/>
      <column hidden="0" type="field" width="-1" name="north"/>
      <column hidden="0" type="field" width="-1" name="azimuth"/>
      <column hidden="0" type="field" width="-1" name="gps_date"/>
      <column hidden="0" type="field" width="-1" name="img_date"/>
      <column hidden="1" type="actions" width="-1"/>
    </columns>
  </attributetableconfig>
  <editform></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from PyQt4.QtGui import QWidget

def my_form_open(dialog, layer, feature):
    geom = feature.geometry()
    control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="altitude" editable="1"/>
    <field name="azimuth" editable="1"/>
    <field name="filepath" editable="1"/>
    <field name="gps_date" editable="1"/>
    <field name="img_date" editable="1"/>
    <field name="latitude" editable="1"/>
    <field name="longitude" editable="1"/>
    <field name="north" editable="1"/>
  </editable>
  <labelOnTop>
    <field name="altitude" labelOnTop="0"/>
    <field name="azimuth" labelOnTop="0"/>
    <field name="filepath" labelOnTop="0"/>
    <field name="gps_date" labelOnTop="0"/>
    <field name="img_date" labelOnTop="0"/>
    <field name="latitude" labelOnTop="0"/>
    <field name="longitude" labelOnTop="0"/>
    <field name="north" labelOnTop="0"/>
  </labelOnTop>
  <widgets/>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <expressionfields/>
  <previewExpression>filepath</previewExpression>
  <mapTip>[% CASE
  WHEN left("filepath", 1) = '/' THEN concat('&lt;img src="file://', "filepath", '" width=200 height=200/>')
  ELSE concat('&lt;img src="file:///', "filepath", '" width=200 height=200/>')
END %]</mapTip>
  <layerGeometryType>0</layerGeometryType>
</qgis>
