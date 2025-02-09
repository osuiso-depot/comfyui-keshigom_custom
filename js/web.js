import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

app.registerExtension({
  name: "comfyui-keshigom_custom",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {

    function populate(text) {
      // widgetsを空にする => [] の状態にしておかないと ComfyWidgetsでのstring型widgetの作成 でエラーになる？
      // textは[empty]または['']が渡される可能性がある。
      // ['']はwidegetsの初期値である
      // [empty]はサーバー側から何も渡されなかった場合である => 何もしない
      if(!Array.isArray(text) || text.length < 1) return;

      if (this.widgets) {
        for (let i = 0; i < this.widgets.length; i++) {
          this.widgets[i].onRemove?.();
        }
        this.widgets.length = 0;
      }

      const v = [...text];

      console.log("populate:", v);

      console.log("node: ", this);
      console.log("node.widgets: ", this.widgets);
      // ComfyWidgets は ComfyUI で提供されるウィジェットのクラス
      // console.log(ComfyWidgets); // 提供される型を確認

      for (const list of v) {
        console.log("add to widgets => ", list)
        const w = ComfyWidgets["STRING"](this, "default", ["STRING", { multiline: true }], app).widget;
        w.value = list;
        console.log("widget created: ", w);
      }

      // widgetsのサイズを再計算。小さくはならない？
      const sz = this.computeSize();
      console.log("computeSize...", sz);

      console.log(this.size[0], this.size[1]);
      this.onResize?.(sz);
      // app.graph.setDirtyCanvas(true, false); // ノード再描画指示 (front, back)

      // requestAnimationFrame(() => {
      //   console.log("requestAnimationFrame...");
      //   const sz = this.computeSize();
      //   console.log("computeSize...");
      //   console.log(sz);

      //   console.log(this.size[0], this.size[1]);
      //   this.onResize?.(sz);
      //   app.graph.setDirtyCanvas(true, false); // ノード再描画指示 (front, back)
      // });

    }

    // onExecuted: execute the node
    // ノードが実行されたときに message.text を表示
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
      onExecuted?.apply(this, arguments);
      // 呼び出し時のnodeTypeをthisで操作する方が自然なので
      // `nodeData.name` ではなく スコープ内の`this.type`を使う
      if (this.type === "KANI_ShowAnything") {
        console.log("this.type", this.type);

        console.log("★onExecuted", message.text);
        populate.call(this, message.text);
      }
    };

    // onConfigure: called after the node has been configured
    const onConfigure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      onConfigure?.apply(this, arguments);
      if (this.type === "KANI_ShowAnything") { // `nodeData.name` ではなく `this.type`
        console.log("★onConfigure");
        if (this.widgets_values?.length) {
          console.log("this.widgets_values:", this.widgets_values);
          populate.call(this, this.widgets_values.slice(this.widgets_values));
        }
      }
    };

    // onNodeCreated: ノードが生成・配置されたときに呼び出されます。また、複数配置されていればそれぞれ呼び出される。
    const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      if (this.type === "KANI_ShowAnything") { // `nodeData.name` ではなく `this.type`
        console.log("★KANI_ShowAnything");

        this.color = "#436";  // 明るい緑色
        this.bgcolor = "#323"; // 濃い緑色
      }
      origOnNodeCreated?.apply(this, arguments);
    };
  }
});
