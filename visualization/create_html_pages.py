import helper
import argparse
import os
import math
from bokeh.palettes import RdBu3
from bokeh.models import ColumnDataSource, LabelSet, DataTable, TableColumn, Div
from bokeh.models.callbacks import CustomJS
from bokeh.models.selections import Selection
from bokeh.io import show
from bokeh.plotting import figure, output_file, save, curdoc
from bokeh.layouts import row, gridplot, layout

BOX_WIDTH = 900
BOX_HEIGHT = 340
TEXT_MAX_LEN = 1000

def main(fpath, opath):
    os.makedirs(opath, exist_ok=True)
    queries = helper.parse_json(fpath)
    for query in queries:
        create_plots(query, opath)

    
def create_plots(query, path):
    output_file('{}/{}_{}.html'.format(path, query['task'], query['id']))
    rankd = query['docs']
    rankp = query['pas']   
    
    # document ranking data
    dscores = [ p['score'] for p in rankd ]
    source_doc = ColumnDataSource(dict(
        doc = [ p['doc_id'] for p in rankd ],
        x = [ p['coord_x'] for p in rankd ],
        y = [ p['coord_y'] for p in rankd ],
        scr = [ round(p['score'], 3) for p in rankd ],
        rad = [ get_circle_size(p['score'], dscores) for p in rankd ],
        color = [ RdBu3[0] for p in rankd ],
        title = [ p['title'] for p in rankd ],
        text = [ p['text'][:TEXT_MAX_LEN]+'...' if len(p['text'])>TEXT_MAX_LEN else p['text'] for p in rankd ],
        authors = [ p['authors'] for p in rankd ],
        journal = [ p['journal'] for p in rankd ],
        url = [ p['url'] for p in rankd ],
        date = [ p['date'] for p in rankd ],
    ))

    # paragraph ranking data
    pscores = [ p['score'] for p in rankp ]
    source_par = ColumnDataSource(dict(
        doc = [ p['doc_id'] for p in rankp ],
        x = [ p['coord_x'] for p in rankp ],
        y = [ p['coord_y'] for p in rankp ],
        scr = [ round(p['score'], 3) for p in rankp ],
        rad = [ get_circle_size(p['score'], pscores) for p in rankp ],
        color = [ RdBu3[2] for p in rankp ],
        title = [ p['title'] for p in rankp ],
        text = [ p['text'] for p in rankp ],
        authors = [ p['authors'] for p in rankp ],
        journal = [ p['journal'] for p in rankp ],
        url = [ p['url'] for p in rankp ],
        date = [ p['date'] for p in rankp ],
    ))

    # plots
    doc_sp = create_scatter_plot(source_doc, True)
    doc_tab = create_table(source_doc, True)
    par_sp = create_scatter_plot(source_par, False)
    par_tab = create_table(source_par, False)

    # selection callbacks
    source_doc.selected.js_on_change('indices', CustomJS(args=dict(sd=source_doc, sp=source_par), code="""
    if (sd.selected.indices.length == 0) {
      return;
    }
    var sel = sd.selected.indices[0];
    var new_selected = [];
    for (var i = 0; i < sp.data['doc'].length; i++) {
      if (sp.data['doc'][i] == sd.data['doc'][sel]) {
        new_selected.push(i);
      }
    }
    if (JSON.stringify(new_selected) != JSON.stringify(sp.selected.indices) &&
    !(sp.selected.indices.length == 1 && new_selected.includes(sp.selected.indices[0]))) {
      sp.selected.indices = new_selected;
      sp.change.emit();
    }
    """))
    source_par.selected.js_on_change('indices', CustomJS(args=dict(sd=source_doc, sp=source_par), code="""
    if (sp.selected.indices.length == 0) {
      return;
    }
    var sel = sp.selected.indices[0];
    var new_selected = [];
    for (var i = 0; i < sd.data['doc'].length; i++) {
      if (sd.data['doc'][i] == sp.data['doc'][sel]) {
        new_selected.push(i);
      }
    }
    if (JSON.stringify(new_selected) != JSON.stringify(sd.selected.indices) &&
    !(sd.selected.indices.length == 1 && new_selected.includes(sd.selected.indices[0]))) {
      sd.selected.indices = new_selected;
      sd.change.emit();
    }
    """))

    # save layout
    save(layout([[Div(text="<h2>{}</h2>".format(query['title']), sizing_mode="stretch_width")],
                   [Div(text="<h3>Document ranking</h3>")], [doc_tab, doc_sp],
                   [Div(text="<h3>Paragraph ranking</h3>")], [par_tab, par_sp]]))
   

def create_scatter_plot(source, isdoc=True):
    tooltips = [
        ("Title", "@title"),
        ("Abstract" if isdoc else "Passage", "@text"),
        ("Published", "@date"),
        ("Authors", "@authors"),
        ("Journal", "@journal"),
        ("URL", "@url")
    ]
    p = figure(x_range=(0, 1), y_range=(0, 1), plot_width=BOX_WIDTH, plot_height=BOX_HEIGHT, tools='tap,reset', tooltips=tooltips, toolbar_location="below")
    p.circle(x='x', y='y', radius='rad', color='color', source=source)
    
    labels = LabelSet(x='x', y='y', text='title', level='glyph', text_font_size="10pt",
                      x_offset=-10, y_offset=5, source=source, render_mode='canvas')
    #p.add_layout(labels)

    return p


def create_table(source, isdoc=True):
    columns = [
        TableColumn(field="scr", title="Score", width=30),
        TableColumn(field=("title" if isdoc else "text"), title=("Document title" if isdoc else "Passage"), width=770),
    ]
    table = DataTable(source=source, columns=columns, width=BOX_WIDTH, height=BOX_HEIGHT)

    return table


def get_circle_size(score, all_scores):
    min_a = 0.0
    max_a = 1.0
    min_b = 0.003
    max_b = 0.02
    return (((score - min_a) / (max_a - min_a)) * (max_b - min_b)) + min_b

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", required=True, help='JSON with all data')
    parser.add_argument("-o", "--outdir", required=True, help='Output directory')
    args = parser.parse_args()
    
    main(args.data, args.outdir)


