public class RawParameterInfo
{
public string Name { get; set; }
public string ID { get; set; }
public string Value { get; set; }
public BuiltInParameterGroup Group { get; set; }
public ParameterType Type { get; set; }
public StorageType Storage { get; set; }
public string Unit { get; set; }
public bool Shared { get; set; }
public bool ReadOnly { get; set; }
}
public static string RawGetDUTString(Parameter p)
{
string unitType = string.Empty;
try { unitType = p.DisplayUnitType.ToString(); }
catch { }
return unitType;
}
public static List<RawParameterInfo> RawGetParametersInfo(Element e)
{
List<RawParameterInfo> paramList =
(from Parameter p in e.Parameters
select new RawParameterInfo
{
Name = p.Definition.Name,
ID = p.IsShared ?
2	p.GUID.ToString() : (p.Definition as InternalDefinition).BuiltInParameter.ToString(),
Value = p.AsValueString(),
Group = p.Definition.ParameterGroup,
Type = p.Definition.ParameterType,
Storage = p.StorageType,
Unit = RawGetDUTString(p),
Shared = p.IsShared,
ReadOnly = p.IsReadOnly,
}).ToList();
return paramList;
}
public static string RawParametersInfoToCSVString<T>(List<T> infoList, ref string title)
{
StringBuilder sb = new StringBuilder();
PropertyInfo[] propInfoArrary = typeof(T).GetProperties();
foreach (PropertyInfo pi in propInfoArrary)
{
title += pi.Name + ",";
}
title = title.Remove(title.Length - 1);
foreach (T info in infoList)
{
foreach (PropertyInfo pi in propInfoArrary)
{
object obj = info.GetType().InvokeMember(pi.Name, BindingFlags.GetProperty, null, info, null);
IList list = obj as IList;
if (list != null)
{
string str = string.Empty;
foreach (object e in list)
{
str += e.ToString() + ";";
}
str = str.Remove(str.Length - 1);
sb.Append(str + ",");
}
else
{
sb.Append((obj == null ?
3	string.Empty : obj.ToString()) + ",");
}
}
sb.Remove(sb.Length - 1, 1).Append(Environment.NewLine);
}
return sb.ToString();
}
public class RawParameterInfo
{
public string Name { get; set; }
public string ID { get; set; }
public string Value { get; set; }
public BuiltInParameterGroup Group { get; set; }
public StorageType Storage { get; set; }
public bool ReadOnly { get; set; }
}
public static string RawGetDUTString(Parameter p)
{
string unitType = string.Empty;
try { unitType = p.DisplayUnitType.ToString(); }
catch { }
return unitType;
}
public static List<RawParameterInfo> RawGetParametersInfo(Element e)
{
List<RawParameterInfo> paramList =
(from Parameter p in e.Parameters
select new RawParameterInfo
{
Name = p.Definition.Name,
ID = p.IsShared ?
4	p.GUID.ToString() : (p.Definition as InternalDefinition).BuiltInParameter.ToString(),
Value = p.AsValueString(),
Group = p.Definition.ParameterGroup,
Storage = p.StorageType,
ReadOnly = p.IsReadOnly,
}).ToList();
return paramList;
}
public static string RawParametersInfoToCSVString<T>(List<T> infoList, ref string title)
{
StringBuilder sb = new StringBuilder();
PropertyInfo[] propInfoArrary = typeof(T).GetProperties();
foreach (PropertyInfo pi in propInfoArrary)
{
title += pi.Name + ",";
}
title = title.Remove(title.Length - 1);
foreach (T info in infoList)
{
foreach (PropertyInfo pi in propInfoArrary)
{
object obj = info.GetType().InvokeMember(pi.Name, BindingFlags.GetProperty, null, info, null);
IList list = obj as IList;
if (list != null)
{
string str = string.Empty;
foreach (object e in list)
{
str += e.ToString() + ";";
}
str = str.Remove(str.Length - 1);
sb.Append(str + ",");
}
else
{
sb.Append((obj == null ?
5	string.Empty : obj.ToString()) + ",");
}
}
sb.Remove(sb.Length - 1, 1).Append(Environment.NewLine);
}
return sb.ToString();
}
Element element = SelElement(cmdData.Application.ActiveUIDocument.Selection).Element;
List<Parameter> paramList = ParametersOf(element);
string str = string.Empty;
foreach (Parameter p in paramList)
{
//The following has to be done because the DUT will throw out exceptions many times!
string unitType = string.Empty;
try { unitType = p.DisplayUnitType.ToString(); }
catch { }
str += string.Format("{0}\tPG:{1}\tPT:{2}\tST:{3}\tDUT:{4}
\tSH:{5}\tID:{6}\tRO:{7}
",
p.Definition.Name,
p.Definition.ParameterGroup,
p.Definition.ParameterType,
p.StorageType,
unitType,
p.IsShared,
p.IsShared ?
6	p.GUID.ToString():(p.Definition as InternalDefinition).BuiltInParameter.ToString(),
p.IsReadOnly);
}
MessageBox.Show(str, "Information of Element Parameters");
public class ParameterInfo
{
public string Name { get; set; }
public string Value { get; set; }
public BuiltInParameterGroup Group { get; set; }
public ParameterType Type { get; set; }
public StorageType Storage { get; set; }
public string Unit { get; set; } //DisplayUnitType doesn't work!
public bool Shared { get; set; }
public string ID { get; set; }
public bool ReadOnly { get; set; }
}
public static List<ParameterInfo> GetParametersInfo(Element e)
{
List<ParameterInfo> paramList =
(from Parameter p in e.Parameters
select new ParameterInfo
{
Name = p.Definition.Name,
Value = p.AsValueString(),
Group = p.Definition.ParameterGroup,
Type = p.Definition.ParameterType,
Storage = p.StorageType,
Unit = GetDUTString(p),
Shared = p.IsShared,
ReadOnly = p.IsReadOnly,
ID = p.IsShared ?
7	p.GUID.ToString() :
(p.Definition as InternalDefinition).BuiltInParameter.ToString()
}).ToList();
return paramList;
}
public string ParametersInfoToCSVString(List<ParameterInfo> infoList, ref string title)
{
StringBuilder sb = new StringBuilder();
PropertyInfo[] propInfoArrary = typeof(ParameterInfo).GetProperties();
foreach (PropertyInfo pi in propInfoArrary)
{
title += pi.Name + ",";
}
title = title.Remove(title.Length - 1);
foreach (ParameterInfo info in infoList)
{
foreach (PropertyInfo pi in propInfoArrary)
{
object obj = info.GetType().InvokeMember(pi.Name, BindingFlags.GetProperty, null, info, null);
sb.Append( (obj == null ?
8	string.Empty : obj.ToString()) + ",");
}
sb.Remove(sb.Length - 1, 1).Append(Environment.NewLine);
}
return sb.ToString();
}
public static Reference SelElement(Selection selection)
{
Reference picked = selection.PickObject(ObjectType.Element, "Please select an element");
return picked;
}
...
Element element = SelElement(cmdData.Application.ActiveUIDocument.Selection).Element;
List<ParameterInfo> paramsInfo = GetParametersInfo(element);
using (StreamWriter sw = new StreamWriter(@"c:\ParametersInfo.csv"))
{
string title = string.Empty;
string rows = ParametersInfoToCSVString(paramsInfo, ref title);
sw.WriteLine(title);
sw.Write(rows);
}
public static Parameter GetParameterWindowHeadHeight(Element e)
{
return e.get_Parameter(BuiltInParameter.INSTANCE_HEAD_HEIGHT_PARAM);
}
public static Parameter GetParameterWindowSillHeight(Element e)
{
return e.get_Parameter(BuiltInParameter.INSTANCE_SILL_HEIGHT_PARAM);
}
public static Parameter GetParameterWindowWidth(Element e)
{
return e.get_Parameter(BuiltInParameter.WINDOW_WIDTH);
}
public static Parameter GetParameterWindowHeight(Element e)
{
return e.get_Parameter(BuiltInParameter.WINDOW_HEIGHT);
}
Element element = SelectElement(cmdData.Application.ActiveUIDocument.Selection).Element;
Element winType = CachedDoc.get_Element(element.GetTypeId());
Parameter p = GetParameterWindowHeadHeight(element);
string str = string.Format("Head height: {0}
", p.AsValueString());
p = GetParameterWindowSillHeight(element);
str += string.Format("Sill height: {0}
", p.AsValueString());
p = GetParameterWindowWidth(winType);
str += string.Format("Window width: {0}
", p.AsValueString());
p = GetParameterWindowHeight(winType);
str += string.Format("Window height: {0}
", p.AsValueString());
MessageBox.Show(str, "Window Parameters");
public static Parameter GetParameterWindowThickness(Element e)
{
return e.get_Parameter(BuiltInParameter.WINDOW_THICKNESS);
}
p = GetParameterWindowThickness(winType);
MessageBox.Show(p.AsValueString(), "Window Thickness");
public static Reference SelectElement(Selection selection)
{
Reference picked = selection.PickObject(ObjectType.Element, new RevitAddinCS.SelectionFilter3(), "Select an element");
return picked;
}
public class SelectionFilter3 : ISelectionFilter
{
public bool AllowElement(Element elem)
{
if (elem.Category.Id.IntegerValue == (int)BuiltInCategory.OST_Windows) return true;
return false;
}
public bool AllowReference(Reference refer, XYZ pos)
{
return true;
}
}
public class RawParameterInfo
{
public string Name { get; set; }
public string ID { get; set; }
public string Value { get; set; }
public BuiltInParameterGroup Group { get; set; }
public ParameterType Type { get; set; }
public StorageType Storage { get; set; }
public string Unit { get; set; }
public bool Shared { get; set; }
public bool ReadOnly { get; set; }
}
public static string RawGetDUTString(Parameter p)
{
string unitType = string.Empty;
try { unitType = p.DisplayUnitType.ToString(); }
catch { }
return unitType;
}
public static List<RawParameterInfo> RawGetParametersInfo(Element e)
{
List<RawParameterInfo> paramList =
(from Parameter p in e.Parameters
select new RawParameterInfo
{
Name = p.Definition.Name,
ID = p.IsShared ?
9	p.GUID.ToString() : (p.Definition as InternalDefinition).BuiltInParameter.ToString(),
Value = p.AsValueString(),
Group = p.Definition.ParameterGroup,
Type = p.Definition.ParameterType,
Storage = p.StorageType,
Unit = RawGetDUTString(p),
Shared = p.IsShared,
ReadOnly = p.IsReadOnly,
}).ToList();
return paramList;
}
public static string RawParametersInfoToCSVString<T>(List<T> infoList, ref string title)
{
StringBuilder sb = new StringBuilder();
PropertyInfo[] propInfoArrary = typeof(T).GetProperties();
foreach (PropertyInfo pi in propInfoArrary)
{
title += pi.Name + ",";
}
title = title.Remove(title.Length - 1);
foreach (T info in infoList)
{
foreach (PropertyInfo pi in propInfoArrary)
{
object obj = info.GetType().InvokeMember(pi.Name, BindingFlags.GetProperty, null, info, null);
IList list = obj as IList;
if (list != null)
{
string str = string.Empty;
foreach (object e in list)
{
str += e.ToString() + ";";
}
str = str.Remove(str.Length - 1);
sb.Append(str + ",");
}
else
{
sb.Append((obj == null ?
10	string.Empty : obj.ToString()) + ",");
}
}
sb.Remove(sb.Length - 1, 1).Append(Environment.NewLine);
}
return sb.ToString();
}
public class RawParameterInfo
{
public string Name { get; set; }
public string ID { get; set; }
public string Value { get; set; }
public BuiltInParameterGroup Group { get; set; }
public StorageType Storage { get; set; }
public bool ReadOnly { get; set; }
}
public static string RawGetDUTString(Parameter p)
{
string unitType = string.Empty;
try { unitType = p.DisplayUnitType.ToString(); }
catch { }
return unitType;
}
public static List<RawParameterInfo> RawGetParametersInfo(Element e)
{
List<RawParameterInfo> paramList =
(from Parameter p in e.Parameters
select new RawParameterInfo
{
Name = p.Definition.Name,
ID = p.IsShared ?