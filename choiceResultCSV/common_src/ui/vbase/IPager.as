package ui.vbase {

	public interface IPager {
		function setParam(index:uint, maxCount:uint):void;
		function set index(value:uint):void;
		function setSelectListener(handler:Function):void;
		function set visible(value:Boolean):void;
	}
}